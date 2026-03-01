export interface GraphProject {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  created_at: Date;
  updated_at: Date;
}

export interface GraphProjectCreate {
  name: string;
  description: string;
}

export interface GraphProjectResponse {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  created_at: Date;
  updated_at: Date;
}

export interface GraphEntity {
  id: string;
  project_id: string;
  external_id: string;
  type: string;
  labels: string[];
  properties: Record<string, any>;
  created_at: Date;
  updated_at: Date;
}

export interface GraphEntityCreate {
  external_id: string;
  type: string;
  labels: string[];
  properties: Record<string, any>;
}

export interface GraphEntityResponse {
  id: string;
  project_id: string;
  external_id: string;
  type: string;
  labels: string[];
  properties: Record<string, any>;
  created_at: Date;
  updated_at: Date;
}

export interface GraphRelation {
  id: string;
  project_id: string;
  source_id: string;
  target_id: string;
  type: string;
  properties: Record<string, any>;
  created_at: Date;
  updated_at: Date;
}

export interface GraphRelationCreate {
  source_id: string;
  target_id: string;
  type: string;
  properties: Record<string, any>;
}

export interface GraphRelationResponse {
  id: string;
  project_id: string;
  source_id: string;
  target_id: string;
  type: string;
  properties: Record<string, any>;
  created_at: Date;
  updated_at: Date;
}

export interface NeighborResponse {
  entities: GraphEntityResponse[];
  relations: GraphRelationResponse[];
}

export interface NeighborQueryParams {
  entity_id: string;
  depth: number;
  limit?: number;
}