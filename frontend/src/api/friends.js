import api from './client'


export const searchUsers = (query) => {
  return api.get('/api/v1/friends/users/', {
    params: {
      search: query,
    },
  })
}


export const getFriends = () => {
  return api.get('/api/v1/friends/')
}


export const sendFriendRequest = (friendId) => {
  return api.post('/api/v1/friends/', {
    friend: friendId,
  })
}


export const updateFriendStatus = (id, status) => {
  return api.patch(`/api/v1/friends/${id}/`, { status })
}


export const deleteFriend = (id) => {
  return api.delete(`/api/v1/friends/${id}/`)
}
