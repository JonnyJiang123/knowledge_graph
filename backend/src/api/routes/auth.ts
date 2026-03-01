import { FastifyPluginAsync } from 'fastify';
import { AuthService } from '../../domain/services/authService';
import { UserCreate, LoginRequest, TokenResponse, UserResponse } from '../../domain/entities/user';

const authService = new AuthService();

const authRoutes: FastifyPluginAsync = async (fastify) => {
  fastify.post(
    '/auth/register',
    {}
  , async (request, reply) => {
    try {
      const user = await authService.register(request.body as any);
      return reply.status(201).send(user);
    } catch (error) {
      return reply.status(400).send({ error: (error as Error).message });
    }
  });

  fastify.post(
    '/auth/login',
    {}
  , async (request, reply) => {
    try {
      const body = request.body as any;
      const tokenResponse = await authService.login(
        body.email,
        body.password
      );
      return reply.status(200).send(tokenResponse);
    } catch (error) {
      return reply.status(401).send({ error: (error as Error).message });
    }
  });
};

export default authRoutes;