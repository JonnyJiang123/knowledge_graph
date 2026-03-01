import { FastifyPluginAsync } from 'fastify';
import { GraphService } from '../../domain/services/graphService';
import { GraphEntityCreate, GraphEntityResponse, GraphRelationCreate, GraphRelationResponse, NeighborResponse } from '../../domain/entities/graph';
import { authenticate } from '../middlewares/authMiddleware';
import { ProjectService } from '../../domain/services/projectService';

const graphService = new GraphService();
const projectService = new ProjectService();

const graphRoutes: FastifyPluginAsync = async (fastify) => {
  // Apply auth middleware to all routes
  fastify.addHook('preHandler', authenticate);

  // Create graph entity
  fastify.post(
    '/graph/projects/:projectId/entities',
    {}
  , async (request, reply) => {
    try {
      const userId = (request as any).userId;
      const { projectId } = request.params as { projectId: string };
      const body = request.body as any;

      // Check project access
      const hasAccess = await projectService.checkProjectAccess(projectId, userId);
      if (!hasAccess) {
        return reply.status(403).send({ error: 'Not authorized to access this project' });
      }

      const entity = await graphService.createEntity(
        projectId,
        body,
        userId
      );
      return reply.status(201).send(entity);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  // Create graph relation
  fastify.post(
    '/graph/projects/:projectId/relations',
    {}
  , async (request, reply) => {
    try {
      const userId = (request as any).userId;
      const { projectId } = request.params as { projectId: string };
      const body = request.body as any;

      // Check project access
      const hasAccess = await projectService.checkProjectAccess(projectId, userId);
      if (!hasAccess) {
        return reply.status(403).send({ error: 'Not authorized to access this project' });
      }

      const relation = await graphService.createRelation(
        projectId,
        body,
        userId
      );
      return reply.status(201).send(relation);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  // List neighbors
  fastify.get(
    '/graph/projects/:projectId/neighbors',
    {}
  , async (request, reply) => {
    try {
      const userId = (request as any).userId;
      const { projectId } = request.params as { projectId: string };
      const query = request.query as { entity_id: string; depth?: string; limit?: string };
      const { entity_id, depth = '1', limit } = query;

      // Check project access
      const hasAccess = await projectService.checkProjectAccess(projectId, userId);
      if (!hasAccess) {
        return reply.status(403).send({ error: 'Not authorized to access this project' });
      }

      const neighbors = await graphService.listNeighbors(
        projectId,
        entity_id,
        parseInt(depth),
        limit ? parseInt(limit) : undefined
      );
      return reply.status(200).send(neighbors);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });
};

export default graphRoutes;