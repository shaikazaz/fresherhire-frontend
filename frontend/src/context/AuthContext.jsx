import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from 'react';

import { api, tokens } from '../api/client.js';

const AuthContext = createContext(null);

function readCachedUser() {
  try {
    return JSON.parse(localStorage.getItem('user'));
  } catch (e) {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readCachedUser);
  const [loading, setLoading] = useState(Boolean(tokens.access));

  const saveUser = useCallback((u) => {
    setUser(u);

    if (u) {
      localStorage.setItem('user', JSON.stringify(u));
    } else {
      localStorage.removeItem('user');
    }
  }, []);

  useEffect(() => {
    if (!tokens.access) {
      setLoading(false);
      return;
    }

    api
      .get('/auth/me/')
      .then((res) => {
        saveUser(res.data);
      })
      .catch(() => {
        // Ignore authentication errors here.
      })
      .finally(() => {
        setLoading(false);
      });
  }, [saveUser]);

  useEffect(() => {
    const onLogout = () => {
      setUser(null);
      localStorage.removeItem('user');
    };

    window.addEventListener('auth:logout', onLogout);

    return () => {
      window.removeEventListener('auth:logout', onLogout);
    };
  }, []);

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login/', {
      email,
      password,
    });

    tokens.set(data.access, data.refresh);
    saveUser(data.user);

    return data.user;
  };

  const register = async (payload) => {
    const { data } = await api.post('/auth/register/', payload);

    tokens.set(data.access, data.refresh);
    saveUser(data.user);

    return data.user;
  };

  const logout = () => {
    tokens.clear();
    saveUser(null);
  };

  const refreshUser = async () => {
    const { data } = await api.get('/auth/me/');

    saveUser(data);

    return data;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}