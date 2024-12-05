import express from 'express';
import swaggerUi from 'swagger-ui-express';
import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';
import yaml from 'js-yaml';

const app = express();

const swaggerFilesPath = './swagger-files';

function loadSwaggerFiles() {
  const files = readdirSync(swaggerFilesPath).filter(file => file.endsWith('.yaml'));
  const swaggerDocs = {};

  files.forEach(file => {
    const name = file.replace('.yaml', '');
    const filePath = join(swaggerFilesPath, file);
    const fileContent = readFileSync(filePath, 'utf8');
    swaggerDocs[name] = yaml.load(fileContent);
  });

  return swaggerDocs;
}

const swaggerDocs = loadSwaggerFiles();

const swaggerUiOptions = {
  explorer: true,
  swaggerOptions: {
    urls: Object.keys(swaggerDocs).map(name => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      url: `/swagger/${name}`
    }))
  }
};

app.use('/docs', swaggerUi.serve, swaggerUi.setup(null, swaggerUiOptions));

app.get('/swagger/:name', (req, res) => {
  const name = req.params.name;
  if (swaggerDocs[name]) {
    res.json(swaggerDocs[name]);
  } else {
    res.status(404).send('Swagger file not found');
  }
});

// Base route to show a generic message
app.get('/', (req, res) => {
  res.send(`
    <h1>API Documentation</h1>
    <p>Access the Swagger UI documentation:</p>
    <ul>
      <li><a href="/docs">Swagger UI Documentation</a></li>
    </ul>
  `);
});

// Start the server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
