export interface SearchDisplayResult {
  id: string;
  title: string;
  content: string;
  source: string;
  kind: "wiki" | "knowledge";
  score?: number | null;
  page?: number | null;
  section?: string | null;
  url?: string | null;
  categories?: string[];
}
