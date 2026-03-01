import fs from 'fs';
import path from 'path';
import { settings } from '../../config';

export class FileStorage {
  private readonly baseDir: string;

  constructor() {
    this.baseDir = settings.uploadBaseDir;
    this.ensureBaseDir();
  }

  private ensureBaseDir(): void {
    const basePath = path.resolve(this.baseDir);
    if (!fs.existsSync(basePath)) {
      fs.mkdirSync(basePath, { recursive: true });
    }
  }

  public async saveFile(file: Buffer, fileName: string, projectId: string): Promise<string> {
    const projectDir = path.join(this.baseDir, `proj-${projectId}`, 'clean');
    this.ensureDir(projectDir);

    const filePath = path.join(projectDir, fileName);
    await fs.promises.writeFile(filePath, file);

    return filePath;
  }

  public async readFile(filePath: string): Promise<Buffer> {
    if (!fs.existsSync(filePath)) {
      throw new Error('File not found');
    }

    return await fs.promises.readFile(filePath);
  }

  public async deleteFile(filePath: string): Promise<void> {
    if (fs.existsSync(filePath)) {
      await fs.promises.unlink(filePath);
    }
  }

  public async listFiles(projectId: string): Promise<string[]> {
    const projectDir = path.join(this.baseDir, `proj-${projectId}`, 'clean');
    if (!fs.existsSync(projectDir)) {
      return [];
    }

    const files = await fs.promises.readdir(projectDir);
    return files.map(file => path.join(projectDir, file));
  }

  private ensureDir(dir: string): void {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  public getFilePath(projectId: string, fileName: string): string {
    return path.join(this.baseDir, `proj-${projectId}`, 'clean', fileName);
  }

  public getPublicUrl(filePath: string): string {
    // In a real-world scenario, this would return a signed URL or public endpoint
    return `/uploads/${path.relative(this.baseDir, filePath)}`;
  }
}
