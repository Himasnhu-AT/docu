export default {
  title: "Docu Documentation",
  description:
    "Documentation generator for Python code using special #/ comments",
  themeConfig: {
    sidebar: [
      {
        text: "Introduction",
        link: "/",
      },
      {
        text: "Contributing",
        collapsed: false,
        items: [
          { text: "Overview", link: "/contributing/" },
          { text: "Code Style", link: "/contributing/code-style" },
          { text: "Pull Requests", link: "/contributing/pull-requests" },
        ],
      },
      {
        text: "Developer Guide",
        collapsed: false,
        items: [
          { text: "Overview", link: "/developers/" },
          { text: "Getting Started", link: "/developers/getting-started" },
          { text: "API Reference", link: "/developers/api-reference" },
        ],
      },
      {
        text: "Architecture",
        collapsed: false,
        items: [
          { text: "Overview", link: "/architecture/" },
          {
            text: "Code Organization",
            link: "/architecture/code-organization",
          },
          { text: "Processing Flow", link: "/architecture/processing-flow" },
        ],
      },
    ],
    nav: [
      { text: "Home", link: "/" },
      { text: "Contributing", link: "/contributing/" },
      { text: "Developer Guide", link: "/developers/" },
      { text: "Architecture", link: "/architecture/" },
      { text: "GitHub", link: "https://github.com/Himasnhu-AT/docu" },
    ],
    socialLinks: [
      { icon: "github", link: "https://github.com/Himasnhu-AT/docu" },
    ],
  },
};
