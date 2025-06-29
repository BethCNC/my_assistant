import React from 'react';
import { ComponentStory, ComponentMeta } from '@storybook/react';
import Card from './Card';

export default {
  title: 'UI/Card',
  component: Card,
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'outlined'],
    },
  },
} as ComponentMeta<typeof Card>;

// Create a template for the stories
const Template: ComponentStory<typeof Card> = (args) => <Card {...args} />;

// Default Card
export const Default = Template.bind({});
Default.args = {
  title: 'Default Card',
  children: <p>This is the content of a default card component.</p>,
  variant: 'default',
};

// Outlined Card
export const Outlined = Template.bind({});
Outlined.args = {
  title: 'Outlined Card',
  children: <p>This is the content of an outlined card component.</p>,
  variant: 'outlined',
}; 