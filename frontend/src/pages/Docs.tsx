import React from "react";
import { FaMusic, FaCommentAlt, FaUser, FaMicrophoneAlt } from "react-icons/fa";
import { RiAlbumFill } from "react-icons/ri";
import { BsFillPostcardHeartFill } from "react-icons/bs";
import ThemeWrapper from "../components/ThemeWrapper";

const Docs: React.FC = () => {
  const redirectToDocs = (path: string) => {
    window.open(`http://localhost:3000/docs/${path}`, "_blank"); //Change to VM IP
  };

  const buttonStyle: React.CSSProperties = {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "3rem",
    backgroundColor: "#1e242b", 
    color: "#FFFFFF",
    borderRadius: "0.75rem",
    boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
    transition: "transform 0.3s ease-in-out, background-color 0.3s ease-in-out",
    cursor: "pointer",
    marginBottom: "2rem",
  };

  const gridStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "2rem",
    maxWidth: "800px",
    margin: "0 auto",
  };

  const wrapperStyle: React.CSSProperties = {
    backgroundColor: "#121212",
    height: "100vh",
    padding: "2rem",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  };

  return (
    <ThemeWrapper>
      <div style={wrapperStyle}>
        <div style={gridStyle}>
          {[
            { icon: <FaMicrophoneAlt size={64} />, label: "Artist", path: "artist" },
            { icon: <RiAlbumFill size={64} />, label: "Album", path: "album" },
            { icon: <FaCommentAlt size={64} />, label: "Comment", path: "comment" },
            { icon: <BsFillPostcardHeartFill size={64} />, label: "Post", path: "post" },
            { icon: <FaMusic size={64} />, label: "Song", path: "song" },
            { icon: <FaUser size={64} />, label: "User", path: "user" },
          ].map(({ icon, label, path }) => (
            <button
              key={path}
              onClick={() => redirectToDocs(path)}
              style={buttonStyle}
              onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.1)")}
              onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
            >
              {icon}
              <div style={{ marginTop: "1rem", fontSize: "1.25rem", fontWeight: "bold" }}>{label}</div>
            </button>
          ))}
        </div>
      </div>
    </ThemeWrapper>
  );
};

export default Docs;
