import { DataTypes, Model } from 'sequelize';
import { sequelize } from '../database';

export class GraphProjectModel extends Model {
  public id!: string;
  public name!: string;
  public description!: string;
  public owner_id!: string;
  public readonly created_at!: Date;
  public readonly updated_at!: Date;
}

GraphProjectModel.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    name: {
      type: DataTypes.STRING(100),
      allowNull: false,
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: true,
    },
    owner_id: {
      type: DataTypes.UUID,
      allowNull: false,
      references: {
        model: 'users',
        key: 'id',
      },
    },
  },
  {
    sequelize,
    tableName: 'graph_projects',
    timestamps: true,
    createdAt: 'created_at',
    updatedAt: 'updated_at',
  },
);
