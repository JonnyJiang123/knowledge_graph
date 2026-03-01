import { FastifyRequest, FastifyReply } from 'fastify';
import { AuthService } from '../../domain/services/authService';

const authService = new AuthService();

export async function authenticate(request: FastifyRequest, reply: FastifyReply) {
  try {
    const authHeader = request.headers.authorization;

    if (!authHeader) {
      return reply.status(401).send({ error: 'Authorization header required' });
    }

    const token = authHeader.split(' ')[1];

    if (!token) {
      return reply.status(401).send({ error: 'Token required' });
    }

    const userId = authService.verifyToken(token);
    const user = await authService.getUserById(userId);

    if (!user) {
      return reply.status(401).send({ error: 'User not found' });
    }

    // Attach user to request object
    (request as any).user = user;
    (request as any).userId = userId;
  } catch (error) {
    return reply.status(401).send({ error: 'Invalid or expired token' });
  }
}
