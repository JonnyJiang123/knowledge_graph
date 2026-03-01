import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';

// Load environment variables
dotenv.config();

export class Settings {
  // App
  public readonly appName: string = process.env.APP_NAME || 'Knowledge Graph Platform';
  public readonly debug: boolean = process.env.DEBUG === 'true';

  // Database
  public readonly mysqlUri: string =
    process.env.MYSQL_URI || 'mysql://root:password@localhost:3306/knowledge_graph';
  public readonly neo4jUri: string = process.env.NEO4J_URI || 'bolt://localhost:7687';
  public readonly neo4jUser: string = process.env.NEO4J_USER || 'neo4j';
  public readonly neo4jPassword: string = process.env.NEO4J_PASSWORD || 'password';
  public readonly redisUri: string = process.env.REDIS_URI || 'redis://localhost:6379';

  // Auth
  public readonly secretKey: string =
    process.env.SECRET_KEY || 'change-this-in-production-use-openssl-rand-hex-32';
  public readonly algorithm: string = process.env.ALGORITHM || 'HS256';
  public readonly accessTokenExpireMinutes: number = parseInt(
    process.env.ACCESS_TOKEN_EXPIRE_MINUTES || '30',
  );

  // Processing
  public readonly syncFileSizeLimit: number = parseInt(
    process.env.SYNC_FILE_SIZE_LIMIT || '5242880',
  ); // 5MB
  public readonly syncRowLimit: number = parseInt(process.env.SYNC_ROW_LIMIT || '10000');
  public readonly uploadBaseDir: string = process.env.UPLOAD_BASE_DIR || 'storage/uploads';
  public readonly tempDir: string = process.env.TEMP_DIR || 'storage/tmp';
  public readonly previewRowLimit: number = parseInt(process.env.PREVIEW_ROW_LIMIT || '50');
  public readonly encryptionKey: string =
    process.env.ENCRYPTION_KEY || 'qsXlU9kZ0w6zKz5g7zxubUoilT0yoyS9MhUlCT3VkOQ=';

  constructor() {
    this.ensureStorageDirs();
  }

  public ensureStorageDirs(): void {
    const uploadPath = path.resolve(this.uploadBaseDir);
    const tempPath = path.resolve(this.tempDir);

    if (!fs.existsSync(uploadPath)) {
      fs.mkdirSync(uploadPath, { recursive: true });
    }

    if (!fs.existsSync(tempPath)) {
      fs.mkdirSync(tempPath, { recursive: true });
    }
  }
}

export const settings = new Settings();
