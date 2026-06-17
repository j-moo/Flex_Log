import api from './client'


// 유저 검색
export const searchUsers = (query) => {
  return api.get('/api/v1/friends/search/', {
    params: {
      q: query,
    },
  })
}


// 친구 목록 조회
export const getFriends = () => {
  return api.get('/api/v1/friends/')
}


// 친구 요청
export const sendFriendRequest = (friendId) => {
  return api.post('/api/v1/friends/', {
    friend: friendId,
  })
}


// 친구 요청 수락/거절
export const updateFriendStatus = (
  id,
  status,
) => {
  return api.patch(
    `/api/v1/friends/${id}/`,
    {
      status,
    },
  )
}