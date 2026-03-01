import { FastifyPluginAsync } from 'fastify';
import { authenticate } from '../middlewares/authMiddleware';

const ingestionRoutes: FastifyPluginAsync = async (fastify) => {
  // Apply auth middleware to all routes
  fastify.addHook('preHandler', authenticate);

  // Ingestion routes
  fastify.post('/ingestion/jobs', async (request, reply) => {
    try {
      // TODO: Implement ingestion job creation
      return reply.status(201).send({ id: '1', status: 'pending' });
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.get('/ingestion/jobs', async (request, reply) => {
    try {
      // TODO: Implement ingestion job listing
      return reply.status(200).send([]);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.get('/ingestion/jobs/:id', async (request, reply) => {
    try {
      // TODO: Implement ingestion job details
      const { id } = request.params as { id: string };
      return reply.status(200).send({ id, status: 'completed' });
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });
};

export default ingestionRoutes;