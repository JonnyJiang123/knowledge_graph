import { settings } from '../../config';
import Bull from 'bull';

// Create task queues
const ingestionQueue = new Bull('ingestion', settings.redisUri);
const extractionQueue = new Bull('extraction', settings.redisUri);
const backupQueue = new Bull('backup', settings.redisUri);

// Define task interfaces
export interface IngestionTask {
  projectId: string;
  dataSource: string;
  options: any;
}

export interface ExtractionTask {
  projectId: string;
  documentId: string;
  options: any;
}

export interface BackupTask {
  projectId: string;
  options: any;
}

// Task processors
ingestionQueue.process(async (job: Bull.Job) => {
  try {
    const task = job.data as IngestionTask;
    console.log(`Processing ingestion task for project ${task.projectId}`);
    // TODO: Implement actual ingestion logic
    await new Promise(resolve => setTimeout(resolve, 5000)); // Simulate processing
    console.log(`Completed ingestion task for project ${task.projectId}`);
    return { success: true, projectId: task.projectId };
  } catch (error) {
    console.error('Error processing ingestion task:', error);
    throw error;
  }
});

extractionQueue.process(async (job: Bull.Job) => {
  try {
    const task = job.data as ExtractionTask;
    console.log(`Processing extraction task for document ${task.documentId}`);
    // TODO: Implement actual extraction logic
    await new Promise(resolve => setTimeout(resolve, 3000)); // Simulate processing
    console.log(`Completed extraction task for document ${task.documentId}`);
    return { success: true, documentId: task.documentId };
  } catch (error) {
    console.error('Error processing extraction task:', error);
    throw error;
  }
});

backupQueue.process(async (job: Bull.Job) => {
  try {
    const task = job.data as BackupTask;
    console.log(`Processing backup task for project ${task.projectId}`);
    // TODO: Implement actual backup logic
    await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate processing
    console.log(`Completed backup task for project ${task.projectId}`);
    return { success: true, projectId: task.projectId };
  } catch (error) {
    console.error('Error processing backup task:', error);
    throw error;
  }
});

// Task queue service
export class TaskQueueService {
  public async addIngestionTask(task: IngestionTask): Promise<string> {
    const job = await ingestionQueue.add(task);
    return job.id.toString();
  }

  public async addExtractionTask(task: ExtractionTask): Promise<string> {
    const job = await extractionQueue.add(task);
    return job.id.toString();
  }

  public async addBackupTask(task: BackupTask): Promise<string> {
    const job = await backupQueue.add(task);
    return job.id.toString();
  }

  public async getTaskStatus(queueName: string, taskId: string): Promise<any> {
    let queue: ReturnType<typeof Bull>;
    switch (queueName) {
      case 'ingestion':
        queue = ingestionQueue;
        break;
      case 'extraction':
        queue = extractionQueue;
        break;
      case 'backup':
        queue = backupQueue;
        break;
      default:
        throw new Error('Invalid queue name');
    }

    const job = await queue.getJob(taskId);
    if (!job) {
      throw new Error('Task not found');
    }

    const state = await job.getState();
    const progress = await job.progress();

    return {
      id: job.id.toString(),
      state,
      progress,
    };
  }

  public async cancelTask(queueName: string, taskId: string): Promise<boolean> {
    let queue: ReturnType<typeof Bull>;
    switch (queueName) {
      case 'ingestion':
        queue = ingestionQueue;
        break;
      case 'extraction':
        queue = extractionQueue;
        break;
      case 'backup':
        queue = backupQueue;
        break;
      default:
        throw new Error('Invalid queue name');
    }

    const job = await queue.getJob(taskId);
    if (!job) {
      return false;
    }

    await job.remove();
    return true;
  }
}

export const taskQueueService = new TaskQueueService();
