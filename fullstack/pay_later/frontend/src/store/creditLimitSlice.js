import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  creditLimit: null,
  loading: false,
  error: null,
};

const creditLimitSlice = createSlice({
  name: 'creditLimits',
  initialState,
  reducers: {
    fetchCreditLimitStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchCreditLimitSuccess: (state, action) => {
      state.loading = false;
      state.creditLimit = action.payload;
    },
    fetchCreditLimitFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    applyCreditLimitStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    applyCreditLimitSuccess: (state, action) => {
      state.loading = false;
      state.creditLimit = action.payload;
    },
    applyCreditLimitFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  fetchCreditLimitStart,
  fetchCreditLimitSuccess,
  fetchCreditLimitFailure,
  applyCreditLimitStart,
  applyCreditLimitSuccess,
  applyCreditLimitFailure,
  clearError,
} = creditLimitSlice.actions;

export default creditLimitSlice.reducer;
