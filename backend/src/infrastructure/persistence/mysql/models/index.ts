import { UserModel } from './user';
import { GraphProjectModel } from './graphProject';

// Define associations
// User has many GraphProjects
UserModel.hasMany(GraphProjectModel, {
  foreignKey: 'owner_id',
  as: 'graph_projects',
});

// GraphProject belongs to User
GraphProjectModel.belongsTo(UserModel, {
  foreignKey: 'owner_id',
  as: 'owner',
});

export {
  UserModel,
  GraphProjectModel,
};