import type { Meta, StoryObj } from '@storybook/react';
import Icon, { IconName } from './Icon';

const meta: Meta<typeof Icon> = {
  title: 'UI/Icon',
  component: Icon,
  parameters: {
    layout: 'centered',
    design: {
      type: 'figma',
      url: 'https://www.figma.com/file/LKQ4FJ4bTnCSjedbRpk931/Sample-File?node-id=0%3A1&t=2Ggd3hQdviSAGnyz-1',
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof Icon>;

// Create a grid of all icons for documentation
export const IconGallery: Story = {
  render: () => {
    const allIcons: IconName[] = [
      'arrow-right',
      'calendar',
      'check', 
      'chevron-down',
      'chevron-left',
      'chevron-right',
      'chevron-up',
      'close',
      'edit',
      'info',
      'menu',
      'notification',
      'plus',
      'search',
      'settings',
      'user',
      'warning',
    ];

    return (
      <div className="grid grid-cols-3 gap-4 md:grid-cols-4 lg:grid-cols-5">
        {allIcons.map((iconName) => (
          <div 
            key={iconName} 
            className="flex flex-col items-center p-4 border rounded-lg"
          >
            <Icon name={iconName} size="lg" />
            <span className="mt-2 text-sm text-gray-600">{iconName}</span>
          </div>
        ))}
      </div>
    );
  },
};

// Individual icon stories
export const Default: Story = {
  args: {
    name: 'info',
    size: 'md',
  },
};

export const Small: Story = {
  args: {
    name: 'info',
    size: 'sm',
  },
};

export const Large: Story = {
  args: {
    name: 'info',
    size: 'lg',
  },
};

export const Colored: Story = {
  args: {
    name: 'warning',
    size: 'lg',
    color: '#f59e0b',
  },
}; 