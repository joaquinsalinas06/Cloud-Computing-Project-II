export interface Pagination {
	currentPage: number;
	pageSize: number;
	hasNextPage: boolean;
	hasPreviousPage: boolean;
	lastEvaluatedKey: string | null;
}
