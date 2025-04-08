export const getImageFromServerSrc = (src: string) => {
  if (process.env.NEXT_PUBLIC_OUTPUT_MODE === "export" && src) {
    return src;
  }

  const basePath = process.env.NEXT_PUBLIC_API_BASEPATH;
  return new URL(src, basePath).href;
};
