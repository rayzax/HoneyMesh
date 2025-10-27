import React from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

// Use require(...).default (or import at top) to get the image URL string
const FeatureList = [
  {
    title: 'Easy to Deploy',
    img: require('@site/static/img/EasyToDeploy_HoneyMesh3.png').default,
    description: (
      <>
        HoneyMesh is built from the ground up to make honeypot deployment simple
        and fast. With just a few commands, you can spin up fully configured honeypots
        using Docker automation. No complex setup required.
      </>
    ),
  },
  {
    title: 'Focus on Threat Intelligence',
    img: require('@site/static/img/HoneyMesh_Laptop.png').default,
    description: (
      <>
       HoneyMesh lets you focus on capturing and analyzing attacker behavior while
        it handles the heavy lifting. It automates container management, log forwarding,
        and monitoring, so you can spend more time learning from real attacks, not managing
        infrastructure.
      </>
    ),
  },
  {
    title: 'Powered by Elastic and Python',
    img: require('@site/static/img/HoneyMesh_Workstation2.png').default,
    description: (
      <>
        Built with Python and the Elastic Stack, HoneyMesh offers a flexible, modern
        foundation for cybersecurity research. Customize dashboards, enrich telemetry,
        and extend honeypot configurations, all while keeping a unified interface for
        visibility and control.
      </>
    ),
  },
];

function Feature({ img, title, description }) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        {/* Render the URL string as an <img> tag */}
        {img && (
          <img
            src={img}
            alt={title}
            className={styles.featureSvg} /* reuse your css class if desired */
            style={{ maxWidth: '100%', height: 'auto' }}
          />
        )}
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
