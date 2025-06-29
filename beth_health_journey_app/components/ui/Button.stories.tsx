import React, { useState, useEffect } from 'react';
import { ComponentStory, ComponentMeta } from '@storybook/react';
import Button from './Button';
import { getFigmaComponentUrl, parseNodeIdFromUrl, parseFileKeyFromUrl } from '../../utils/figmaUtils';

export default {
  title: 'UI/Button',
  component: Button,
  parameters: {
    design: {
      type: 'figma',
      url: 'https://www.figma.com/file/fuNPYw6oQL52ooGCfVzhVI/beth-health-journey-website-components?node-id=2031-60850',
    },
    docs: {
      description: {
        component: `
## Button Component

The Button component is used to trigger actions or events when clicked.

### Usage Guidelines
- Use the Primary variant for main actions
- Use Secondary for alternative actions
- Use Outline for less prominent actions
- Use Text for the least prominent actions

### Figma Component
This component is linked to the Button component in our Figma design system.
        `,
      },
    },
  },
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'outline', 'text'],
      description: 'The visual style of the button',
      table: {
        defaultValue: { summary: 'primary' },
      },
    },
    size: {
      control: { type: 'select' },
      options: ['sm', 'md', 'lg'],
      description: 'The size of the button',
      table: {
        defaultValue: { summary: 'md' },
      },
    },
    isFullWidth: { 
      control: 'boolean',
      description: 'Whether the button should take full width',
    },
    isDisabled: { 
      control: 'boolean',
      description: 'Whether the button is disabled',
    },
    isLoading: { 
      control: 'boolean',
      description: 'Whether the button is in loading state',
    },
    onClick: { action: 'clicked' },
  },
} as ComponentMeta<typeof Button>;

// Create a template for the stories
const Template: ComponentStory<typeof Button> = (args) => <Button {...args} />;

// Primary Button
export const Primary = Template.bind({});
Primary.args = {
  variant: 'primary',
  children: 'Primary Button',
};
Primary.parameters = {
  design: {
    type: 'figma',
    url: 'https://www.figma.com/file/fuNPYw6oQL52ooGCfVzhVI/beth-health-journey-website-components?node-id=2031-60850',
  },
};

// Secondary Button
export const Secondary = Template.bind({});
Secondary.args = {
  variant: 'secondary',
  children: 'Secondary Button',
};
Secondary.parameters = {
  design: {
    type: 'figma',
    url: 'https://www.figma.com/file/LKQ4FJ4bTnCSjedbRpk931/Sample-File?node-id=0%3A2',
  },
};

// Outline Button
export const Outline = Template.bind({});
Outline.args = {
  variant: 'outline',
  children: 'Outline Button',
};
Outline.parameters = {
  design: {
    type: 'figma',
    url: 'https://www.figma.com/file/LKQ4FJ4bTnCSjedbRpk931/Sample-File?node-id=0%3A3',
  },
};

// Text Button
export const Text = Template.bind({});
Text.args = {
  variant: 'text',
  children: 'Text Button',
};
Text.parameters = {
  design: {
    type: 'figma',
    url: 'https://www.figma.com/file/LKQ4FJ4bTnCSjedbRpk931/Sample-File?node-id=0%3A4',
  },
};

// Loading Button
export const Loading = Template.bind({});
Loading.args = {
  isLoading: true,
  children: 'Loading...',
};

// Disabled Button
export const Disabled = Template.bind({});
Disabled.args = {
  isDisabled: true,
  children: 'Disabled Button',
};

// Small Button
export const Small = Template.bind({});
Small.args = {
  size: 'sm',
  children: 'Small Button',
};

// Large Button
export const Large = Template.bind({});
Large.args = {
  size: 'lg',
  children: 'Large Button',
};

// Full Width Button
export const FullWidth = Template.bind({});
FullWidth.args = {
  isFullWidth: true,
  children: 'Full Width Button',
};

// This example demonstrates how to use the MCP Figma API to fetch specific component data
export const WithFigmaData: ComponentStory<typeof Button> = (args) => {
  const [figmaData, setFigmaData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [downloadStatus, setDownloadStatus] = useState('');

  const fetchFigmaComponent = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Use the MCP Figma API to fetch component data
      const response = await mcp_figma_get_figma_data({
        fileKey: "fuNPYw6oQL52ooGCfVzhVI",
        nodeId: "2031:60850",
        depth: 1 // Limit depth to keep payload size manageable
      });
      setFigmaData(response);
    } catch (err) {
      setError(err.message || 'Failed to fetch Figma data');
    } finally {
      setIsLoading(false);
    }
  };

  const downloadComponentImage = async () => {
    setDownloadStatus('Downloading...');
    try {
      // Download the component image
      await mcp_figma_download_figma_images({
        fileKey: "fuNPYw6oQL52ooGCfVzhVI",
        nodes: [
          {
            nodeId: "2031:60850",
            fileName: "button-component.png"
          }
        ],
        localPath: "public/figma-images"
      });
      setDownloadStatus('Download complete!');
    } catch (err) {
      setDownloadStatus(`Download failed: ${err.message || 'Unknown error'}`);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Button {...args}>Figma Button</Button>
      
      <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
        <button onClick={fetchFigmaComponent} disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Fetch Figma Data'}
        </button>
        <button onClick={downloadComponentImage} disabled={isLoading}>
          Download Component Image
        </button>
      </div>
      
      {downloadStatus && (
        <div style={{ marginTop: '10px' }}>{downloadStatus}</div>
      )}
      
      {error && (
        <div style={{ color: 'red', marginTop: '10px' }}>Error: {error}</div>
      )}
      
      {figmaData && (
        <div style={{ marginTop: '10px' }}>
          <h3>Figma Component Data:</h3>
          <pre style={{ 
            maxHeight: '400px', 
            overflow: 'auto', 
            background: '#f5f5f5', 
            padding: '10px',
            borderRadius: '4px'
          }}>
            {JSON.stringify(figmaData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

WithFigmaData.args = {
  ...Primary.args
};

WithFigmaData.parameters = {
  design: {
    type: 'figma',
    url: 'https://www.figma.com/file/fuNPYw6oQL52ooGCfVzhVI/beth-health-journey-website-components?node-id=2031-60850'
  }
}; 