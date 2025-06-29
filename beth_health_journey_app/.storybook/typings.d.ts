// This file exists to help TypeScript understand Storybook modules
declare module '*.stories.tsx' {
  const Stories: any;
  export default Stories;
}

declare module '*.stories.mdx' {
  const MDX: any;
  export default MDX;
} 