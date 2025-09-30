import React from 'react';
import { UserInfo } from './types';

interface UserInfoCardProps {
  user: UserInfo;
}

export const UserInfoCard: React.FC<UserInfoCardProps> = ({ user }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Пользователь</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-600">Имя</label>
          <p className="mt-1 text-lg font-semibold">{user.first_name}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600">Фамилия</label>
          <p className="mt-1 text-lg font-semibold">{user.last_name}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600">login</label>
          <p className="mt-1 text-lg font-semibold">{user.username}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600">e-mail</label>
          <p className="mt-1 text-lg font-semibold">{user.email}</p>
        </div>
      </div>
    </div>
  );
};