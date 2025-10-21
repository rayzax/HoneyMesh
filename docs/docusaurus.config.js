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
<!-- TailwindCSS (only include once globally in your layout or mkdocs.yml) -->
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.3/dist/tailwind.min.css" rel="stylesheet">

<footer class="bg-slate-900 text-slate-200">
  <div class="max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-4 gap-8">
    
    <!-- Logo + About -->
    <div class="space-y-4">
      <div class="flex items-start gap-4">
        <img src="/assets/HoneyMesh_Logo.png" alt="HoneyMesh Logo" class="w-28 h-auto">
        <div>
          <h3 class="text-lg font-semibold">Across the States Bank</h3>
          <p class="text-sm text-slate-400">Superior service. Global reach.</p>
        </div>
      </div>
      <p class="text-sm text-slate-400">
        Banking solutions for individuals and businesses — secure, reliable, and accessible.
      </p>

      <div class="flex items-center gap-3 mt-2">
        <a href="#" aria-label="Facebook" class="p-2 rounded-md hover:bg-slate-800" title="Facebook">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 12.07C22 6.48 17.52 2 11.93 2 6.34 2 1.86 6.48 1.86 12.07 1.86 17.09 5.85 21.14 10.68 21.98v-6.99H8.44v-2.92h2.24V9.31c0-2.21 1.32-3.42 3.34-3.42.97 0 1.99.17 1.99.17v2.18h-1.12c-1.1 0-1.44.68-1.44 1.38v1.66h2.45l-.39 2.92h-2.06V21.98C18.15 21.14 22 17.09 22 12.07z" fill="currentColor"/>
          </svg>
        </a>
        <a href="#" aria-label="Twitter" class="p-2 rounded-md hover:bg-slate-800" title="Twitter">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 5.92c-.6.27-1.24.46-1.92.55.69-.41 1.21-1.06 1.45-1.84-.65.39-1.37.68-2.14.84C18.96 4.6 18 4 16.89 4c-1.6 0-2.9 1.3-2.9 2.9 0 .23.03.45.08.66C10.01 7.44 6.13 5.5 3.36 2.47c-.25.43-.39.93-.39 1.46 0 1.01.51 1.9 1.29 2.43-.48-.02-.93-.15-1.33-.36v.04c0 1.4.99 2.57 2.31 2.84-.24.06-.5.09-.76.09-.19 0-.37-.02-.55-.05.37 1.16 1.44 2.01 2.71 2.03C7.5 13.8 6 14.4 4.38 14.4c-.27 0-.54-.02-.8-.05 1.52.98 3.32 1.55 5.26 1.55 6.31 0 9.77-5.23 9.77-9.76v-.45c.67-.48 1.25-1.09 1.71-1.78-.62.27-1.28.45-1.96.53z" fill="currentColor"/>
          </svg>
        </a>
        <a href="#" aria-label="Instagram" class="p-2 rounded-md hover:bg-slate-800" title="Instagram">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm5 6.5A4.5 4.5 0 1 0 16.5 13 4.5 4.5 0 0 0 12 8.5zm6.6-3.1a1.1 1.1 0 1 0 1.1 1.1 1.1 1.1 0 0 0-1.1-1.1z" fill="currentColor"/>
          </svg>
        </a>
        <a href="#" aria-label="LinkedIn" class="p-2 rounded-md hover:bg-slate-800" title="LinkedIn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20.45 20.45h-3.6v-5.6c0-1.34-.03-3.07-1.87-3.07-1.87 0-2.16 1.46-2.16 2.97v5.7h-3.6V9h3.46v1.56h.05c.48-.9 1.65-1.86 3.4-1.86 3.63 0 4.3 2.39 4.3 5.5v6.8zM5.34 7.43a2.09 2.09 0 1 1 0-4.18 2.09 2.09 0 0 1 0 4.18zM7.14 20.45H3.5V9h3.64v11.45z" fill="currentColor"/>
          </svg>
        </a>
      </div>
    </div>

    <!-- Quick Links -->
    <div>
      <h4 class="font-semibold mb-3">Quick Links</h4>
      <ul class="space-y-2 text-sm text-slate-400">
        <li><a href="#" class="hover:text-white">Home</a></li>
        <li><a href="#" class="hover:text-white">Personal Banking</a></li>
        <li><a href="#" class="hover:text-white">Business Banking</a></li>
        <li><a href="#" class="hover:text-white">Support</a></li>
        <li><a href="#" class="hover:text-white">Careers</a></li>
      </ul>
    </div>

    <!-- Resources -->
    <div>
      <h4 class="font-semibold mb-3">Resources</h4>
      <ul class="space-y-2 text-sm text-slate-400">
        <li><a href="#" class="hover:text-white">Security Center</a></li>
        <li><a href="#" class="hover:text-white">Rates & Fees</a></li>
        <li><a href="#" class="hover:text-white">Locations</a></li>
        <li><a href="#" class="hover:text-white">Blog</a></li>
        <li><a href="#" class="hover:text-white">FAQ</a></li>
      </ul>
    </div>

    <!-- Newsletter -->
    <div>
      <h4 class="font-semibold mb-3">Stay informed</h4>
      <p class="text-sm text-slate-400 mb-3">Get occasional product updates and security tips.</p>
      <form class="flex gap-2" onsubmit="alert('Subscribed!'); return false;">
        <label for="footer-email" class="sr-only">Email address</label>
        <input id="footer-email" type="email" placeholder="you@domain.com" required class="w-full rounded-md px-3 py-2 bg-slate-800 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500">
        <button type="submit" class="px-4 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white">Subscribe</button>
      </form>

      <div class="mt-6 text-sm text-slate-400">
        <a href="#" class="block hover:text-white">Privacy Policy</a>
        <a href="#" class="block hover:text-white">Terms of Service</a>
        <a href="#" class="block hover:text-white">Accessibility</a>
      </div>
    </div>
  </div>

  <div class="border-t border-slate-800">
    <div class="max-w-7xl mx-auto px-6 py-4 flex flex-col md:flex-row justify-between items-center text-sm text-slate-400">
      <div>© 2025 Across the States Bank. All rights reserved.</div>
      <div class="flex items-center gap-4 text-xs">
        <div>Security: SSL / TLS</div>
        <div>Site map</div>
        <div>Contact: (555) 555-5555</div>
      </div>
    </div>
  </div>
</footer>




export default config;
