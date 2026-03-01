import fastify from 'fastify';
import cors from 'fastify-cors';
import helmet from '@fastify/helmet';
import rateLimit from '@fastify/rate-limit';
import swagger from '@fastify/swagger';
import swaggerUI from '@fastify/swagger-ui';
import staticPlugin from '@fastify/static';
import path from 'path';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Import routes
import authRoutes from './api/routes/auth';
import projectRoutes from './api/routes/projects';
import graphRoutes from './api/routes/graph';
import ingestionRoutes from './api/routes/ingestion';
import entityRoutes from './api/routes/entities';
import relationRoutes from './api/routes/relations';
import queryRoutes from './api/routes/query';
import visualizationRoutes from './api/routes/visualization';
import extractionRoutes from './api/routes/extraction';

// Import config
import { settings } from './config';

// Import database connections
import { Neo4jClient } from './infrastructure/persistence/neo4j/client';
import { RedisClient } from './infrastructure/cache/redis';
import { testConnection } from './infrastructure/persistence/mysql/database';

// Create Fastify instance
const app = fastify({
  logger: {
    level: settings.debug ? 'debug' : 'info',
    transport: {
      target: 'pino-pretty',
      options: {
        colorize: true,
      },
    },
  },
});

// Register plugins
app.register(cors, {
  origin: 'http://localhost:3000',
  credentials: true,
  methods: ['*'],
  allowedHeaders: ['*'],
});

app.register(helmet);

app.register(rateLimit, {
  max: 100,
  timeWindow: '1 minute',
});

app.register(swagger, {
  swagger: {
    info: {
      title: settings.appName,
      version: '0.2.0',
      description: 'Knowledge Graph Platform API',
    },
    tags: [
      { name: 'auth', description: 'Authentication routes' },
      { name: 'projects', description: 'Project management routes' },
      { name: 'graph', description: 'Graph operations routes' },
      { name: 'ingestion', description: 'Data ingestion routes' },
      { name: 'entities', description: 'Entity operations routes' },
      { name: 'relations', description: 'Relation operations routes' },
      { name: 'query', description: 'Query operations routes' },
      { name: 'visualization', description: 'Visualization routes' },
      { name: 'extraction', description: 'Knowledge extraction routes' },
    ],
  },
});

app.register(swaggerUI, {
  routePrefix: '/docs',
});

// Register static file serving
app.register(staticPlugin, {
  root: path.join(__dirname, '../../storage/uploads'),
  prefix: '/uploads/',
});

// Register routes
app.register(authRoutes, { prefix: '/api' });
app.register(projectRoutes, { prefix: '/api' });
app.register(graphRoutes, { prefix: '/api' });
app.register(ingestionRoutes, { prefix: '/api' });
app.register(entityRoutes, { prefix: '/api' });
app.register(relationRoutes, { prefix: '/api' });
app.register(queryRoutes, { prefix: '/api' });
app.register(visualizationRoutes, { prefix: '/api' });
app.register(extractionRoutes, { prefix: '/api' });

// Health check route
app.get('/health', async () => {
  return {
    status: 'healthy',
    version: '0.2.0',
    features: [
      'graph_management',
      'query',
      'visualization',
      'extraction',
    ],
  };
});

// Root route
app.get('/', async () => {
  return {
    message: 'Knowledge Graph Platform API',
    version: '0.2.0',
    docs: '/docs',
  };
});

// Lifecycle hooks
app.addHook('onReady', async () => {
  try {
      await Neo4jClient.connect();
      app.log.info('Neo4j connected successfully');
    } catch (error) {
      app.log.error(`Failed to connect to Neo4j: ${error}`);
    }

    try {
      RedisClient.connect();
      app.log.info('Redis connected successfully');
    } catch (error) {
      app.log.error(`Failed to connect to Redis: ${error}`);
    }

    try {
      await testConnection();
      app.log.info('MySQL connected successfully');
    } catch (error) {
      app.log.error(`Failed to connect to MySQL: ${error}`);
    }
});

app.addHook('onClose', async () => {
  try {
    await Neo4jClient.disconnect();
    app.log.info('Neo4j disconnected successfully');
  } catch (error) {
    app.log.error(`Failed to disconnect from Neo4j: ${error}`);
  }

  try {
    RedisClient.disconnect();
    app.log.info('Redis disconnected successfully');
  } catch (error) {
    app.log.error(`Failed to disconnect from Redis: ${error}`);
  }
});

// Start server
const PORT = process.env.PORT || 8000;
app.listen({ port: parseInt(PORT as string), host: '0.0.0.0' }, (err) => {
  if (err) {
    app.log.error(err);
    process.exit(1);
  }
  app.log.info(`Server running at http://localhost:${PORT}`);
  app.log.info(`Swagger docs available at http://localhost:${PORT}/docs`);
});

export default app;