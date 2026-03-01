import { FastifyPluginAsync } from 'fastify';
import { authenticate } from '../middlewares/authMiddleware';

const queryRoutes: FastifyPluginAsync = async (fastify) => {
  // Apply auth middleware to all routes
  fastify.addHook('preHandler', authenticate);

  // Query routes
  fastify.get('/graph/search', async (request, reply) => {
    try {
      // TODO: Implement entity search
      return reply.status(200).send([]);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.post('/graph/paths', async (request, reply) => {
    try {
      // TODO: Implement path finding
      return reply.status(200).send([]);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });
};

export default queryRoutes;