import neo4j, { Driver, Session } from 'neo4j-driver';
import { settings } from '../../../config';

export class Neo4jClient {
  private static driver: Driver | null = null;

  public static async connect(): Promise<void> {
    try {
      this.driver = neo4j.driver(
        settings.neo4jUri,
        neo4j.auth.basic(settings.neo4jUser, settings.neo4jPassword)
      );

      // Verify connection
      if (this.driver) {
        await this.driver.verifyConnectivity();
        console.log('Neo4j connection established');
      }
    } catch (error) {
      console.error('Failed to connect to Neo4j:', error);
      throw error;
    }
  }

  public static async disconnect(): Promise<void> {
    if (this.driver) {
      await this.driver.close();
      this.driver = null;
      console.log('Neo4j connection closed');
    }
  }

  public static getDriver(): Driver {
    if (!this.driver) {
      throw new Error('Neo4j driver not initialized');
    }
    return this.driver;
  }

  public static getSession(): Session {
    return this.getDriver().session();
  }

  public static async executeQuery(query: string, params?: Record<string, any>): Promise<any> {
    const session = this.getSession();
    try {
      const result = await session.run(query, params);
      return result.records;
    } finally {
      await session.close();
    }
  }
}