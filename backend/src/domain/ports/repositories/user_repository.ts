import { User } from '@/domain/entities/user';

export interface UserRepository {
  createUser(user: User): Promise<User>;
  getUser(id: string): Promise<User | null>;
  getUserByEmail(email: string): Promise<User | null>;
  updateUser(user: User): Promise<User>;
  deleteUser(id: string): Promise<boolean>;
  listUsers(limit?: number, offset?: number): Promise<User[]>;
  existsUser(id: string): Promise<boolean>;
  existsUserByEmail(email: string): Promise<boolean>;
}
