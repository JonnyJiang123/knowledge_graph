export interface Task {
  id: string;
  type: string;
  payload: Record<string, any>;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  createdAt: Date;
  updatedAt: Date;
}

export interface TaskQueue {
  enqueue(taskType: string, payload: Record<string, any>): Promise<string>;
  getTaskStatus(taskId: string): Promise<Task>;
  cancelTask(taskId: string): Promise<boolean>;
  listTasks(status?: string, limit?: number, offset?: number): Promise<Task[]>;
}
