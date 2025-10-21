// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'HoneyMesh',
  tagline: 'Empowering cybersecurity professionals, students, and researchers with an accessible, automated, customizable honeypot framework that makes threat intelligence and proactive security practices more accessible.',
  favicon: 'img/HoneyMesh_PictureLogo.png',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://HoneyMesh.readthedocs.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/en/latest/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'rayzax', // Usually your GitHub org/user name.
  projectName: 'HoneyMesh', // Usually your repo name.

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/rayzax/HoneyMesh',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/rayzax/HoneyMesh',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/HoneyMesh_PictureLogo.png',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'HoneyMesh',
        logo: {
          alt: 'HoneyMesh logo',
          src: 'img/HoneyMesh_PictureLogo.png',
        },
        
      },
footer: {
  style: 'dark',
  links: [
    {
      title: 'Documentation',
      items: [
        {
          label: 'Getting Started',
          to: '/docs/intro',
        },
        {
          label: 'Deployment Guide',
          to: '/docs/deployment',
        },
        {
          label: 'Configuration',
          to: '/docs/configuration',
        },
      ],
    },
    {
      title: 'Community',
      items: [
        {
          label: 'GitHub Discussions',
          href: 'https://github.com/rayzax/HoneyMesh/discussions',
        },
        {
          label: 'Report Issues',
          href: 'https://github.com/rayzax/HoneyMesh/issues',
        },
        {
          label: 'Contribute',
          to: '/docs/contributing',
        },
      ],
    },
    {
      title: 'Resources',
      items: [
        {
          label: 'Blog',
          to: '/blog',
        },
        {
          label: 'Project Repository',
          href: 'https://github.com/rayzax/HoneyMesh',
        },
        {
          label: 'ReadTheDocs',
          href: 'https://honeymesh.readthedocs.io',
        },
      ],
    },
  ],

  logo: {
    alt: 'HoneyMesh Logo',
    src: 'img/HoneyMesh_PictureLogo.png',
    href: 'https://HoneyMesh.readthedocs.io',
    width: 80,
    height: 80,
  },

  copyright: `
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="/img/HoneyMesh_PictureLogo.png" alt="HoneyMesh logo" class="footer-logo" />
        <p>Empowering cybersecurity professionals, students, and researchers through open-source honeypot automation and analysis.</p>
      </div>

      <div class="footer-social">
        <a href="https://github.com/rayzax/HoneyMesh" target="_blank" rel="noopener" aria-label="GitHub">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.09 3.29 9.41 7.86 10.94.58.11.79-.25.79-.56v-2.05c-3.2.7-3.88-1.54-3.88-1.54-.53-1.35-1.3-1.71-1.3-1.71-1.07-.74.08-.73.08-.73 1.18.08 1.8 1.21 1.8 1.21 1.05 1.81 2.77 1.29 3.44.99.11-.77.41-1.29.75-1.59-2.55-.29-5.24-1.27-5.24-5.66 0-1.25.45-2.27 1.19-3.07-.12-.29-.52-1.45.11-3.02 0 0 .97-.31 3.18 1.17.92-.26 1.9-.38 2.88-.39.98 0 1.96.13 2.88.39 2.21-1.48 3.18-1.17 3.18-1.17.63 1.57.23 2.73.11 3.02.74.8 1.19 1.82 1.19 3.07 0 4.41-2.7 5.36-5.27 5.65.42.36.8 1.06.8 2.13v3.15c0 .31.21.68.8.56A10.98 10.98 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z"/></svg>
        </a>
      </div>
    </div>

    <p class="footer-bottom">© ${new Date().getFullYear()} HoneyMesh. Built with Docusaurus.</p>
  `,
  },
      



export default config;
