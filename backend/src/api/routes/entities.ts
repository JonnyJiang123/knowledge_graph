import { FastifyPluginAsync } from 'fastify';
import { authenticate } from '../middlewares/authMiddleware';

const entityRoutes: FastifyPluginAsync = async (fastify) => {
  // Apply auth middleware to all routes
  fastify.addHook('preHandler', authenticate);

  // Entity routes
  fastify.get('/entities', async (request, reply) => {
    try {
      // TODO: Implement entity listing
      return reply.status(200).send([]);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.get('/entities/:id', async (request, reply) => {
    try {
      // TODO: Implement entity details
      const { id } = request.params as { id: string };
      return reply.status(200).send({ id, name: 'Entity' });
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });
};

export default entityRoutes;