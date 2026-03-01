import { UserRepository } from '@/domain/ports/repositories/user_repository';
import { User } from '@/domain/entities/user';
import { UserModel } from './models/user';

export class MySQLUserRepository implements UserRepository {
  async createUser(user: User): Promise<User> {
    const userModel = new UserModel({
      id: user.id,
      username: user.username,
      email: user.email,
      password: user.password,
      created_at: user.created_at,
      updated_at: user.updated_at,
    });

    await userModel.save();
    return this.mapToDomain(userModel);
  }

  async getUser(id: string): Promise<User | null> {
    const userModel = await UserModel.findByPk(id);
    if (!userModel) {
      return null;
    }
    return this.mapToDomain(userModel);
  }

  async getUserByEmail(email: string): Promise<User | null> {
    const userModel = await UserModel.findOne({ where: { email } });
    if (!userModel) {
      return null;
    }
    return this.mapToDomain(userModel);
  }

  async updateUser(user: User): Promise<User> {
    const userModel = await UserModel.findByPk(user.id);
    if (!userModel) {
      throw new Error('User not found');
    }

    userModel.username = user.username;
    userModel.email = user.email;
    userModel.password = user.password;

    await userModel.save();
    return this.mapToDomain(userModel);
  }

  async deleteUser(id: string): Promise<boolean> {
    const result = await UserModel.destroy({ where: { id } });
    return result > 0;
  }

  async listUsers(limit?: number, offset?: number): Promise<User[]> {
    const query: any = {};
    if (limit) {
      query.limit = limit;
    }
    if (offset) {
      query.offset = offset;
    }

    const userModels = await UserModel.findAll(query);
    return userModels.map((model: UserModel) => this.mapToDomain(model));
  }

  async existsUser(id: string): Promise<boolean> {
    const count = await UserModel.count({ where: { id } });
    return count > 0;
  }

  async existsUserByEmail(email: string): Promise<boolean> {
    const count = await UserModel.count({ where: { email } });
    return count > 0;
  }

  private mapToDomain(model: UserModel): User {
    return {
      id: model.id,
      username: model.username,
      email: model.email,
      password: model.password,
      created_at: model.created_at,
      updated_at: model.updated_at,
    };
  }
}
