import { FastifyPluginAsync } from 'fastify';
import { ProjectService } from '../../application/services/project_service';
import { GraphProjectCreate } from '../../domain/entities/graph';
import { authenticate } from '../middlewares/authMiddleware';

// TODO: Use dependency injection
const projectService = new ProjectService();

const projectRoutes: FastifyPluginAsync = async fastify => {
  // Apply auth middleware to all routes
  fastify.addHook('preHandler', authenticate);

  fastify.post('/projects', {}, async (request, reply) => {
    try {
      const userId = (request as any).userId;
      const { name, description } = request.body as GraphProjectCreate;
      const project = await projectService.createProject(name, description, userId);
      return reply.status(201).send(project);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.get('/projects', {}, async (request, reply) => {
    try {
      const userId = (request as any).userId;
      const projects = await projectService.listProjects(userId);
      return reply.status(200).send(projects);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.get('/projects/:id', {}, async (request, reply) => {
    try {
      const { id } = request.params as { id: string };
      const project = await projectService.getProject(id);
      if (!project) {
        return reply.status(404).send({ error: 'Project not found' });
      }
      return reply.status(200).send(project);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.put('/projects/:id', {}, async (request, reply) => {
    try {
      const { id } = request.params as { id: string };
      const { name, description } = request.body as any;
      const project = await projectService.updateProject(id, name, description);
      if (!project) {
        return reply.status(404).send({ error: 'Project not found' });
      }
      return reply.status(200).send(project);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.delete('/projects/:id', {}, async (request, reply) => {
    try {
      const { id } = request.params as { id: string };
      const success = await projectService.deleteProject(id);
      if (!success) {
        return reply.status(404).send({ error: 'Project not found' });
      }
      return reply.status(200).send({ success });
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });
};

export default projectRoutes;
