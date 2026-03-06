---
icon: lucide/home
title: Kubernetes Guide (Clear Explanations + Practical Examples)
description: A modern Kubernetes learning guide with clear explanations of pods, deployments, services, ingress, security, and operations—plus practical examples.
hide:
  - footer
---

# 

<meta name="google-adsense-account" content="ca-pub-4744916432619667">

<div style="text-align: center;">

<img src="/images/logo-v2.png" width="20%">

</div>

<br><br>

Welcome to the **Kubernetes Guide**, a quick and easy-to-digest summary of core Kubernetes concepts intended to help get you from zero to proficient!

<br>

> **Note:** This site focuses on clear explanations and practical learning. For official specifications and upstream documentation, see the [Kubernetes Documentation](https://kubernetes.io/docs/).


<style>
.newsletter-container {
  max-width: 550px;
  margin: 2rem auto;
  padding: 1.75rem;
  border-radius: 14px;
  background: var(--md-default-bg-color);
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
  border: 1px solid rgba(0,0,0,0.06);
}

.newsletter-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
}

.newsletter-subtitle {
  font-size: 0.9rem;
  color: var(--md-default-fg-color--light);
  margin-bottom: 1rem;
}

.newsletter-form {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.newsletter-input {
  flex: 1;
  min-width: 220px;
  padding: 0.7rem 0.8rem;
  border-radius: 8px;
  border: 1px solid rgba(0,0,0,0.15);
  font-size: 0.9rem;
  outline: none;
  transition: border 0.2s ease, box-shadow 0.2s ease;
}

.newsletter-input:focus {
  border-color: var(--md-primary-fg-color);
  box-shadow: 0 0 0 2px rgba(63,81,181,0.15);
}

.newsletter-button {
  padding: 0.7rem 1.1rem;
  border-radius: 8px;
  border: none;
  background: var(--md-primary-fg-color);
  color: white;
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: transform 0.05s ease, box-shadow 0.15s ease;
}

.newsletter-button:hover {
  box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}

.newsletter-footer {
  font-size: 0.75rem;
  margin-top: 0.7rem;
  color: var(--md-default-fg-color--lighter);
}

.newsletter-footer a {
  color: var(--md-primary-fg-color);
  text-decoration: none;
}
</style>


<div class="newsletter-container">

<div class="newsletter-title">
Subscribe to the Kubernetes Newsletter
</div>

<div class="newsletter-subtitle">
Short, practical Kubernetes insights for engineers and platform teams.
</div>

<form
  action="https://buttondown.com/api/emails/embed-subscribe/braundmeier"
  method="post"
  class="newsletter-form"
  referrerpolicy="unsafe-url"
>
  <input 
    type="email"
    name="email"
    placeholder="Enter your email"
    required
    class="newsletter-input"
  />

  <button type="submit" class="newsletter-button">
    Subscribe
  </button>
</form>

<div class="newsletter-footer">
</div>

</div>

<br><br>

## Start Learning Kubernetes

If you're new to Kubernetes, start with these core concepts and build your understanding step by step:

- [Kubernetes Overview](getting-started/overview/)
- [Pods vs Deployments](workloads/pods-deployments/)
- [Kubernetes Services](networking/services-networking/)
- [Ingress and Traffic Routing](networking/ingress/)
- [Kubernetes Security Fundamentals](security/security/)


<br><br>

!!! info "Support"

    k8s.guide is a free Kubernetes learning site I created and maintain in my spare time.

    If it’s helped you, consider supporting it to help offset hosting and maintenance costs. Thanks for your support!

    <a href="https://buymeacoffee.com/braundmeier" target="_blank" rel="noopener">
      <img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png"
          alt="Buy Me A Coffee"
          style="height:50px;width:217px;border:0;">
    </a>

<br>
