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
themeConfig: /** @type {import('@docusaurus/preset-classic').ThemeConfig} */ 
  ({ // Replace with your project's social card i
    image: 'img/HoneyMesh_PictureLogo.png', 
    colorMode: { 
      respectPrefersColorScheme: true,
    },
    navbar: { 
      title: 'HoneyMesh',
      logo: { 
        alt: 'HoneyMesh logo', src: 'img/HoneyMesh_PictureLogo.png',
      },
    },
  
footer: {
  style: 'dark',
  links: [
    {
      // Mission statement as a full-width block above the logo
      title: '',
      items: [
        {
          html: `
            <div class="footer-mission-statement">
              Empowering cybersecurity professionals, students, and researchers with an accessible, automated, customizable honeypot framework that makes threat intelligence and proactive security practices more accessible.
            </div>
          `,
        },
      ],
    },
    {
      // Logo
      title: '',
      items: [
        {
          html: `
            <div class="footer-logo-wrapper">
              <a href="/">
                <img src="img/HoneyMesh_PictureLogo.png" alt="HoneyMesh Logo" width="100" height="100"/>
              </a>
            </div>
          `,
        },
      ],
    },
    {
      title: 'Navigation and Quick Links',
      items: [
        { label: 'Home', to: '/docs/welcome' },
        { label: 'About Us', to: '/docs/what-is-honeymesh' },
        { label: 'FAQs', to: '/docs/faqs' },
      ],
    },
    {
      title: 'Contact Us',
      items: [
        { label: 'Email Us', href: 'mailto:honeymeshinc@gmail.com' },
        { label: 'Call Us', href: 'tel:+11234567890' },
        { label: 'Support Hours: M-F 9am-5pm', href: '#' },
      ],
    },
    {
      title: 'Connect With Us',
      items: [
        { label: 'GitHub', href: 'https://github.com/rayzax/HoneyMesh' },
        { label: 'X', href: 'https://x.com/HoneyMeshInc' },
        { label: 'Instagram', href: 'https://www.instagram.com/honeymeshinc/' },
      ],
    },
    {
      title: 'Newsletter',
      items: [
        {
          html: `
            <div class="footer-subscribe-wrapper">
              <form class="footer-subscribe-form" onsubmit="event.preventDefault(); alert('Subscribed!');">
                <input type="email" placeholder="Your email" required class="footer-email-input" />
                <button type="submit" class="footer-subscribe-button">Subscribe</button>
              </form>
            </div>
          `,
        },
      ],
    },
  ],
  copyright: `Copyright © ${new Date().getFullYear()} HoneyMesh, Inc. Built with Docusaurus.`,
}

export default config;
