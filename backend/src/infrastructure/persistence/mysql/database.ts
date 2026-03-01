import { Sequelize } from 'sequelize';
import { settings } from '../../../config';

// Parse MySQL URI to get connection details
const parseMySQLUri = (uri: string): any => {
  const match = uri.match(/mysql:\/\/(\w+):(\w+)@(\w+):(\d+)\/(\w+)/);
  if (!match) {
    throw new Error('Invalid MySQL URI');
  }
  return {
    username: match[1],
    password: match[2],
    host: match[3],
    port: parseInt(match[4]),
    database: match[5],
  };
};

const mysqlConfig = parseMySQLUri(settings.mysqlUri);

export const sequelize = new Sequelize({
  dialect: 'mysql',
  host: mysqlConfig.host,
  port: mysqlConfig.port,
  username: mysqlConfig.username,
  password: mysqlConfig.password,
  database: mysqlConfig.database,
  logging: settings.debug ? console.log : false,
  pool: {
    max: 10,
    min: 0,
    acquire: 30000,
    idle: 10000,
  },
});

// Test connection
export const testConnection = async (): Promise<void> => {
  try {
    await sequelize.authenticate();
    console.log('MySQL connection established');
  } catch (error) {
    console.error('Failed to connect to MySQL:', error);
    throw error;
  }
};
