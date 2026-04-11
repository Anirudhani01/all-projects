import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import userReducer from './userSlice';
import transactionReducer from './transactionSlice';
import creditLimitReducer from './creditLimitSlice';

const store = configureStore({
  reducer: {
    auth: authReducer,
    user: userReducer,
    transactions: transactionReducer,
    creditLimits: creditLimitReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export default store;
