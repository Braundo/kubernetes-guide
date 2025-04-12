---
icon: material/school-outline
---

# Kubernetes Certification Preparation

The CNCF offers several certifications to validate your Kubernetes knowledge. This section helps you prepare for the **three core exams**:

- [Certified Kubernetes Administrator (CKA)](cka.md)
- [Certified Kubernetes Application Developer (CKAD)](ckad.md)
- [Certified Kubernetes Security Specialist (CKS)](cks.md)

Each guide includes:
- Core topics you need to master
- Trusted resources and courses
- Practical exam tips and environment setup

---

## Exam Overview

| Cert | Duration | Format       | Focus Area              |
|------|----------|--------------|--------------------------|
| CKA  | 2 hours  | Hands-on lab | Cluster operations, admin |
| CKAD | 2 hours  | Hands-on lab | App design, deployment   |
| CKS  | 2 hours  | Hands-on lab | Security and hardening   |

---

## General Advice

- Practice in a real cluster — don’t rely only on theory
- Learn to navigate `kubectl` quickly — alias everything
- Master `vim`, `tmux`, and `kubectl explain`
- Use tab-complete and `kubectl -h` constantly
- Use `--dry-run=client -o yaml` for rapid manifest generation

---

## Resources

### Books

| Book Title               | Link                                                                                           |
|--------------------------|-----------------------------------------------------------------------------------------------|
| Kubernetes Up & Running  | [Kubernetes Up & Running](https://amzn.to/3XX7uaG){target="_blank"} |
| The Kubernetes Book      | [The Kubernetes Book](https://amzn.to/41sLaqy){target="_blank"}     |
| Certified Kubernetes Administrator Study Guide | [Certified Kubernetes Administrator Study Guide](https://amzn.to/4hkpoex){target="_blank"} |
| Quick Start Kubernetes | [Quick Start Kubernetes](https://amzn.to/4bBZAt8){target="_blank"} |
| Networking & Kubernetes | [Networking & Kubernetes](https://amzn.to/4hBuYt3){target="_blank"} |
| Kubernetes Best Practices | [Kubernetes Best Practices](https://amzn.to/4iBuunT){target="_blank"} |
| The Book of Kubernetes | [The Book of Kubernetes](https://amzn.to/3Fy3Nlv){target="_blank"} |

### Documentation

| Description                        | Link                                      |
|------------------------------------|-------------------------------------------|
| Official Kubernetes documentation. | [Kubernetes Documentation](https://kubernetes.io/docs/){target="_blank"} |

### Online Courses

| Course                              | Link                                                                                           |
|-------------------------------------|-----------------------------------------------------------------------------------------------|
| CKA Course on Udemy                 | [CKA Course on Udemy](https://www.udemy.com/course/certified-kubernetes-administrator/){target="_blank"}       |
| CKAD Design & Build on Pluralsight | [CKAD Design & Build on Pluralsight](https://www.pluralsight.com/courses/ckad-application-design-build-cert){target="_blank"} |

### Practice Labs

| Description                     | Link                                                                                           |
|---------------------------------|-----------------------------------------------------------------------------------------------|
| Katacoda                       | [Katacoda](https://www.katacoda.com/){target="_blank"}                                                          |
| Play with Kubernetes           | [Play with Kubernetes](https://labs.play-with-k8s.com/){target="_blank"}                                        |
| Killer Shell  | [killer.sh](https://killer.sh/){target="_blank"} |

> Note: You’ll have access to [kubernetes.io/docs](https://kubernetes.io/docs) and [github.com/kubernetes](https://github.com/kubernetes) during the exam.

---

## Ready to Dive In?

Choose your path:

- 👉 [CKA – Admin-focused](cka.md)
- 👉 [CKAD – Developer-focused](ckad.md)
- 👉 [CKS – Security-focused](cks.md)