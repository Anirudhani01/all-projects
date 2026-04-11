import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  transactions: [],
  currentTransaction: null,
  loading: false,
  error: null,
};

const transactionSlice = createSlice({
  name: 'transactions',
  initialState,
  reducers: {
    fetchTransactionsStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchTransactionsSuccess: (state, action) => {
      state.loading = false;
      state.transactions = action.payload;
    },
    fetchTransactionsFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    fetchTransactionStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchTransactionSuccess: (state, action) => {
      state.loading = false;
      state.currentTransaction = action.payload;
    },
    fetchTransactionFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    createTransactionStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    createTransactionSuccess: (state, action) => {
      state.loading = false;
      state.transactions.unshift(action.payload);
    },
    createTransactionFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  fetchTransactionsStart,
  fetchTransactionsSuccess,
  fetchTransactionsFailure,
  fetchTransactionStart,
  fetchTransactionSuccess,
  fetchTransactionFailure,
  createTransactionStart,
  createTransactionSuccess,
  createTransactionFailure,
  clearError,
} = transactionSlice.actions;

export default transactionSlice.reducer;
