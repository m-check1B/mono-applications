const load = async ({ parent }) => {
  const parentData = await parent();
  const sessionId = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const userId = "user_123";
  const companyId = "company_456";
  return {
    ...parentData,
    sessionId,
    userId,
    companyId
  };
};
export {
  load
};
