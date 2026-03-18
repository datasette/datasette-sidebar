export interface StarItem {
  id: string;
  star_type: string;
  database_name: string;
  table_name: string | null;
  row_pks: string | null;
  created_at: string;
}

export interface TableInfo {
  name: string;
  columns: string[];
  count: number;
  hidden: boolean;
}

export interface DatabaseInfo {
  name: string;
  path: string;
  tables: TableInfo[];
}
