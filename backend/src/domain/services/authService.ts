import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { UserCreate, UserResponse, TokenResponse } from '../entities/user';
import { UserModel } from '../../infrastructure/persistence/mysql/models/user';
import { settings } from '../../config';

export class AuthService {
  public async register(userData: UserCreate): Promise<UserResponse> {
    // Check if user already exists
    const existingUser = await UserModel.findOne({
      where: { email: userData.email },
    });

    if (existingUser) {
      throw new Error('User with this email already exists');
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(userData.password, 10);

    // Create user
    const user = await UserModel.create({
      username: userData.username,
      email: userData.email,
      password: hashedPassword,
    });

    return this.mapToUserResponse(user);
  }

  public async login(email: string, password: string): Promise<TokenResponse> {
    // Find user
    const user = await UserModel.findOne({
      where: { email },
    });

    if (!user) {
      throw new Error('Invalid email or password');
    }

    // Verify password
    const isPasswordValid = await bcrypt.compare(password, user.password);

    if (!isPasswordValid) {
      throw new Error('Invalid email or password');
    }

    // Generate token
    const token = this.generateToken(user.id);

    return {
      access_token: token,
      token_type: 'bearer',
      user: this.mapToUserResponse(user),
    };
  }

  public async getUserById(id: string): Promise<UserResponse | null> {
    const user = await UserModel.findByPk(id);

    if (!user) {
      return null;
    }

    return this.mapToUserResponse(user);
  }

  private generateToken(userId: string): string {
    const payload = {
      sub: userId,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + settings.accessTokenExpireMinutes * 60,
    };

    return jwt.sign(payload, settings.secretKey, {
      algorithm: settings.algorithm as jwt.Algorithm,
    });
  }

  public verifyToken(token: string): string {
    try {
      const payload = jwt.verify(token, settings.secretKey, {
        algorithms: [settings.algorithm as jwt.Algorithm],
      }) as any;

      return payload.sub;
    } catch (error) {
      throw new Error('Invalid or expired token');
    }
  }

  private mapToUserResponse(user: UserModel): UserResponse {
    return {
      id: user.id,
      username: user.username,
      email: user.email,
      created_at: user.created_at,
      updated_at: user.updated_at,
    };
  }
}
