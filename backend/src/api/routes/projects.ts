import { FastifyPluginAsync } from 'fastify';
import { ProjectService } from '../../domain/services/projectService';
import { GraphProjectCreate, GraphProjectResponse } from '../../domain/entities/graph';
import { authenticate } from '../middlewares/authMiddleware';

const projectService = new ProjectService();

const projectRoutes: FastifyPluginAsync = async (fastify) => {
  // Apply auth middleware to all routes
  fastify.addHook('preHandler', authenticate);

  fastify.post(
    '/projects',
    {}
  , async (request, reply) => {
    try {
      const userId = (request as any).userId;
      const project = await projectService.createProject(
        request.body as any,
        userId
      );
      return reply.status(201).send(project);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.get(
    '/projects',
    {}
  , async (request, reply) => {
    try {
      const userId = (request as any).userId;
      const projects = await projectService.getProjectsByOwner(userId);
      return reply.status(200).send(projects);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.get(
    '/projects/:id',
    {}
  , async (request, reply) => {
    try {
      const { id } = request.params as { id: string };
      const project = await projectService.getProjectById(id);
      if (!project) {
        return reply.status(404).send({ error: 'Project not found' });
      }
      return reply.status(200).send(project);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.put(
    '/projects/:id',
    {}
  , async (request, reply) => {
    try {
      const userId = (request as any).userId;
      const { id } = request.params as { id: string };
      const project = await projectService.updateProject(
        id,
        request.body as any,
        userId
      );
      if (!project) {
        return reply.status(404).send({ error: 'Project not found or access denied' });
      }
      return reply.status(200).send(project);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.delete(
    '/projects/:id',
    {}
  , async (request, reply) => {
    try {
      const userId = (request as any).userId;
      const { id } = request.params as { id: string };
      const success = await projectService.deleteProject(
        id,
        userId
      );
      if (!success) {
        return reply.status(404).send({ error: 'Project not found or access denied' });
      }
      return reply.status(200).send({ success });
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });
};

export default projectRoutes;