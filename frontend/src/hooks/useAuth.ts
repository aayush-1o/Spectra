import { useContext } from 'react'
import { AuthContext } from '../store/auth'

export function useAuth() {
    return useContext(AuthContext)
}
