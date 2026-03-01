import { FastifyPluginAsync } from 'fastify';
import { GraphService } from '../../domain/services/graphService';

import { authenticate } from '../middlewares/authMiddleware';
import { ProjectService } from '../../application/services/project_service';

const graphService = new GraphService();
// TODO: Use dependency injection
const projectService = new ProjectService();

const graphRoutes: FastifyPluginAsync = async fastify => {
  // Apply auth middleware to all routes
  fastify.addHook('preHandler', authenticate);

  // Create graph entity
  fastify.post('/graph/projects/:projectId/entities', {}, async (request, reply) => {
    try {
      const { projectId } = request.params as { projectId: string };
      const body = request.body as any;

      // Check project exists
      const project = await projectService.getProject(projectId);
      if (!project) {
        return reply.status(404).send({ error: 'Project not found' });
      }
      // TODO: Add proper access control
      // For now, we'll just check if the project exists

      const entity = await graphService.createEntity(projectId, body, 'system');
      return reply.status(201).send(entity);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  // Create graph relation
  fastify.post('/graph/projects/:projectId/relations', {}, async (request, reply) => {
    try {
      const { projectId } = request.params as { projectId: string };
      const body = request.body as any;

      // Check project exists
      const project = await projectService.getProject(projectId);
      if (!project) {
        return reply.status(404).send({ error: 'Project not found' });
      }
      // TODO: Add proper access control
      // For now, we'll just check if the project exists

      const relation = await graphService.createRelation(projectId, body, 'system');
      return reply.status(201).send(relation);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  // List neighbors
  fastify.get('/graph/projects/:projectId/neighbors', {}, async (request, reply) => {
    try {
      const { projectId } = request.params as { projectId: string };
      const query = request.query as { entity_id: string; depth?: string; limit?: string };
      const { entity_id, depth = '1', limit } = query;

      // Check project exists
      const project = await projectService.getProject(projectId);
      if (!project) {
        return reply.status(404).send({ error: 'Project not found' });
      }
      // TODO: Add proper access control
      // For now, we'll just check if the project exists

      const neighbors = await graphService.listNeighbors(
        projectId,
        entity_id,
        parseInt(depth),
        limit ? parseInt(limit) : undefined,
      );
      return reply.status(200).send(neighbors);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });
};

export default graphRoutes;
