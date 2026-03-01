import Redis from 'ioredis';
import { settings } from '../../config';

export class RedisClient {
  private static client: Redis | null = null;

  public static connect(): void {
    try {
      this.client = new Redis(settings.redisUri);

      this.client.on('error', error => {
        console.error('Redis error:', error);
      });

      this.client.on('connect', () => {
        console.log('Redis connection established');
      });
    } catch (error) {
      console.error('Failed to connect to Redis:', error);
      throw error;
    }
  }

  public static disconnect(): void {
    if (this.client) {
      this.client.quit();
      this.client = null;
      console.log('Redis connection closed');
    }
  }

  public static getClient(): Redis {
    if (!this.client) {
      throw new Error('Redis client not initialized');
    }
    return this.client;
  }

  public static async set(key: string, value: any, expire?: number): Promise<void> {
    const client = this.getClient();
    const stringValue = typeof value === 'object' ? JSON.stringify(value) : value;

    if (expire) {
      await client.set(key, stringValue, 'EX', expire);
    } else {
      await client.set(key, stringValue);
    }
  }

  public static async get(key: string): Promise<any> {
    const client = this.getClient();
    const value = await client.get(key);

    if (!value) return null;

    try {
      return JSON.parse(value);
    } catch {
      return value;
    }
  }

  public static async del(key: string): Promise<void> {
    const client = this.getClient();
    await client.del(key);
  }

  public static async exists(key: string): Promise<boolean> {
    const client = this.getClient();
    const result = await client.exists(key);
    return result > 0;
  }
}
