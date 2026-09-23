# Enterprise IT Knowledge Base - 10 detailed articles
# Each 300-500 words, covering a distinct IT support scenario

articles = [
{
    "kb_id": 'KB-101',
    "title": 'VPN Troubleshooting Guide',
    "category": 'Networking',
    "tags": ['VPN', 'Remote Access'],
    "last_updated": '2026-07-15',
    "priority": 'Low',
    "version": '1.1',
    "author": 'Network Team',
    "content": """Overview
This guide covers common VPN connectivity issues faced by remote employees and how to resolve them without escalating to IT support. VPN reliability is critical for remote and hybrid staff, since it is often the only path to internal systems, shared drives, and internal applications while working outside the office. Most VPN problems fall into a small number of predictable categories, and the majority can be resolved by the employee directly within a few minutes using the steps below.

Symptoms
Users may experience the VPN client failing to connect entirely, repeated disconnections every few minutes even after a successful login, noticeably slow speeds while connected compared to the office network, or being unable to reach internal resources such as shared drives or internal websites despite the client showing a connected status. Some users also report the client hanging on a "negotiating security settings" screen indefinitely, or receiving certificate warnings that were not present previously.

Troubleshooting Steps
First, confirm your internet connection is stable by loading a website outside the VPN entirely, since a VPN cannot function properly on top of an already unstable connection. Next, restart the VPN client completely by closing it from the system tray rather than simply clicking reconnect, as a full restart clears cached session state that a simple reconnect does not. Check that your VPN client is on the latest version, as outdated clients frequently fail to negotiate security settings with newer gateway configurations. If you are on public WiFi, be aware that some networks actively block VPN ports; try switching to a mobile hotspot to confirm whether the network itself is the problem. Clear the VPN configuration cache and re-enter your credentials if the client shows a certificate error, since expired local certificates are a common and easily fixed cause. If you can connect but cannot reach internal resources, check whether split tunneling is enabled incorrectly, which can route internal traffic outside the tunnel by mistake.

Resolution
Most connectivity issues resolve after a full restart of the VPN client and confirming the latest version is installed, which together resolve the large majority of reported cases. If problems persist after completing all steps above, the issue is likely on the gateway side rather than your local machine, and should be escalated to network administration with the exact error message, a timestamp, and whether the issue is isolated to you or affects colleagues as well."""
},
{
    "kb_id": 'KB-102',
    "title": 'Resetting Your Network Password',
    "category": 'Password Reset',
    "tags": ['Password Reset', 'Account Lockout'],
    "last_updated": '2026-06-30',
    "priority": 'High',
    "version": '1.2',
    "author": 'Identity & Access Team',
    "content": """Overview
Employees are occasionally locked out of their accounts due to expired or forgotten passwords, and this is one of the most common support requests across the organization. This article explains the self-service reset process so most employees can resolve the issue themselves without waiting on a support ticket. Understanding why lockouts happen also helps prevent repeat occurrences.

Symptoms
You may see a message stating your password has expired and prompting an immediate change, or receive repeated login failures despite entering what you believe is the correct password. Some users also encounter a lockout message after several failed attempts, which is a security measure that temporarily disables the account rather than a sign of a technical fault. Occasionally, a password that worked yesterday stops working today with no message explaining why, which usually indicates a scheduled expiration.

Troubleshooting Steps
Navigate to the self-service password portal and select forgot password from the login screen. Enter your employee ID and the email address currently registered to your account, since using an old or personal email will cause the reset to fail silently. A reset link will typically be sent within a few minutes; check your spam or junk folder if it does not arrive, as corporate mail filters occasionally flag automated reset emails. When creating a new password, ensure it meets the complexity requirements: at least twelve characters, including one uppercase letter, one number, and one special character. Avoid reusing any of your last five passwords, as the system will silently reject repeats without always explaining why the new password was not accepted. If you are attempting this from a personal device rather than a company laptop, confirm you are on a network that can reach the reset portal, as some personal networks block corporate authentication traffic.

Resolution
Once reset, allow up to fifteen minutes for the new password to fully sync across all connected systems, including email, VPN, and internal applications, since propagation is not always instantaneous. Attempting to log in immediately after a reset before this window has passed is the most common reason a "successful" reset still appears to fail. If you remain locked out after this window has passed, contact IT support directly, as your account may require a manual unlock that cannot be completed through self-service."""
},
{
    "kb_id": 'KB-103',
    "title": 'Network Firewall Configuration',
    "category": 'Networking',
    "tags": ['Firewall', 'Network', 'Security'],
    "last_updated": '2026-07-01',
    "priority": 'Medium',
    "version": '1.3',
    "author": 'Network Team',
    "content": """Overview
This guide explains how firewall rules affect application connectivity and what to do when a required service is being blocked unexpectedly. Firewalls are a critical layer of network security, but they occasionally block legitimate business traffic, particularly after policy updates or when new tools are introduced without a corresponding exception request. Understanding this process helps employees resolve blocked-application issues faster and through the correct channel.

Symptoms
Applications may fail to connect to external services, show generic timeout errors with no further explanation, or be unable to reach certain internal servers while other network traffic continues to work normally. This selective failure pattern, where some services work and others do not, is usually a strong indicator of a firewall rule rather than a broader network outage. Some employees also notice that a tool worked fine yesterday and stopped working today with no local changes made, which typically points to a recent policy update.

Troubleshooting Steps
First identify which specific application and destination are affected, including the port number if it is known, since firewall exceptions are granted at this level of specificity rather than broadly. Check whether the issue is isolated to your machine or affects your entire team, which is an important distinguishing signal: a team-wide issue indicates a broader firewall rule change, while an isolated issue suggests a local misconfiguration or a machine-specific policy difference. Review any recent firewall policy announcements from network administration that may have changed default behavior, since teams are usually notified in advance of major changes. For internal tools specifically, confirm the tool's required ports against the current whitelist maintained by network administration, as internal tooling occasionally changes its required ports during updates without wide notice.

Resolution
If a legitimate business application is being blocked, submit a firewall exception request through the standard IT portal, including the application name, destination IP address or domain, the specific port number required, and a clear business justification for the access. Exception requests are typically reviewed within one to two business days depending on the sensitivity of the access requested. Temporary local firewall changes should never be made independently without formal approval, even as a short-term workaround, since unauthorized changes can expose the network to real security risk and are difficult to track during incident response."""
},
{
    "kb_id": 'KB-104',
    "title": 'Outlook Email Sync Issues',
    "category": 'Email',
    "tags": ['Email', 'Outlook', 'Sync'],
    "last_updated": '2026-07-10',
    "priority": 'Low',
    "version": '1.0',
    "author": 'Collaboration Tools Team',
    "content": """Overview
This article addresses common Outlook synchronization problems where new emails fail to appear, outgoing mail gets stuck, or the desktop and mobile experience fall out of sync with each other. Sync issues are among the most disruptive email problems since they are not always obvious until an important message is missed entirely, so it is worth understanding the common root causes.

Symptoms
Outlook may show as connected in the status bar but not display new incoming messages that have clearly already arrived based on notifications on other devices. Outgoing mail may get stuck in a permanent "sending" state that never resolves on its own. Some users notice a mismatch between the desktop application and the mobile app, where one shows messages the other does not, which usually points to a sync delay rather than a lost message. In more severe cases, Outlook may become unresponsive entirely when switching between folders.

Troubleshooting Steps
Restart Outlook completely rather than simply refreshing the inbox, since a soft refresh does not always clear a stuck sync process. Independently check your internet connection outside of Outlook to rule out a broader connectivity issue rather than an application-specific one. Verify your mailbox is not near its storage quota, since full or nearly full mailboxes can silently block new mail delivery without always displaying a clear warning message. If corruption is suspected, particularly after an unexpected shutdown or crash, the local Outlook data file may need to be rebuilt, which resolves persistent sync failures that survive a simple restart. Confirm your account credentials have not expired or require reauthentication, particularly if multi-factor authentication was recently enabled or reconfigured on your account, as this can silently break background sync until re-authenticated.

Resolution
Most sync issues resolve with a full application restart combined with a check of mailbox storage, which together account for the majority of reported cases. If the local data file is found to be corrupted, IT can provide a clean rebuild without losing any existing emails, provided the account is properly backed up first, which is standard practice before any data file operation. Persistent issues after these steps should be reported with the exact time the sync stopped working and any error codes displayed."""
},
{
    "kb_id": 'KB-105',
    "title": 'Laptop Overheating and Shutdown Issues',
    "category": 'Hardware',
    "tags": ['Hardware', 'Laptop', 'Overheating'],
    "last_updated": '2026-06-20',
    "priority": 'High',
    "version": '1.1',
    "author": 'Hardware Support Team',
    "content": """Overview
Laptops shutting down unexpectedly or feeling excessively hot during normal use are usually caused by a combination of dust buildup, excessive background processes, or a failing cooling component, and identifying which of these applies determines whether the fix is something you can do yourself or requires physical hardware service. Overheating left unaddressed can shorten the lifespan of internal components significantly.

Symptoms
The device may shut down without warning during intensive tasks such as video calls or large file operations, feel noticeably hot to the touch even during comparatively light use like document editing, or have a fan that runs constantly at high speed regardless of workload. Some users also notice a burning smell or unusual vibration, which should be treated as more urgent and reported immediately rather than troubleshot independently.

Troubleshooting Steps
Check for excessive background processes using the task manager, as runaway applications consuming high CPU are a common and easily overlooked cause of overheating that has nothing to do with the physical hardware. Ensure vents are not blocked by placing the laptop on a hard, flat surface rather than a bed, cushion, or lap, all of which restrict airflow significantly and are a surprisingly common root cause. If the device is more than two years old, physical dust buildup inside the fan assembly becomes increasingly likely and typically requires a professional cleaning rather than a software fix. Update to the latest firmware and BIOS version available for your model, as thermal management bugs are occasionally identified and fixed in these updates. Consider whether the device has recently been used in a notably warmer environment than usual, such as direct sunlight or an un-air-conditioned space, since ambient temperature meaningfully affects cooling performance.

Resolution
If overheating persists after closing unnecessary applications and confirming proper ventilation, the device should be sent for a physical inspection, since internal dust buildup or a failing fan cannot be resolved through software alone and continued use in this state risks permanent hardware damage. Devices showing signs of physical damage, unusual smells, or vibration should be taken out of service immediately rather than waiting for a scheduled inspection."""
},
{
    "kb_id": 'KB-106',
    "title": 'Installing and Licensing Software Requests',
    "category": 'Software',
    "tags": ['Software', 'License', 'Installation'],
    "last_updated": '2026-07-05',
    "priority": 'Medium',
    "version": '1.2',
    "author": 'Application Support Team',
    "content": """Overview
This article explains the process for requesting new software installations and resolving the most common license activation errors that follow. Because company devices are locked down for security reasons, most software cannot simply be installed directly by employees, and understanding the approval workflow helps set the right expectations for how long a request will take.

Symptoms
Software may fail to install due to permission restrictions, displaying a generic access denied message rather than clearly stating that administrator rights are required. Some applications show a license activation error immediately on first launch, even though the company holds a valid license for that tool. Others display a trial expired message despite the employee never having used a personal trial version, which usually indicates the license was not correctly applied rather than a genuine expiration.

Troubleshooting Steps
Confirm you have submitted a software request through the internal IT portal, as most applications require pre-approval before installation is technically possible on a managed company device, regardless of whether you have local admin rights. If installation fails specifically due to permissions, this almost always means administrator rights are required for that installer, which standard user accounts intentionally do not have by default as a security control. For license activation errors specifically, verify you are connected to the company network or VPN at the moment of activation, since many license servers only validate against devices reachable on the internal network and will fail silently otherwise. If the license error appears intermittently rather than consistently, this can indicate the license pool for that application is temporarily exhausted rather than a problem with your specific account.

Resolution
Standard software requests are typically fulfilled within one business day once formally approved through the portal, though complex or higher-cost software may take longer pending budget approval. License activation errors experienced while on VPN usually resolve within a few minutes of reconnecting and relaunching the application. Persistent errors after confirming network connectivity should be reported with the exact error code shown, as this significantly speeds up diagnosis compared to a general description of the problem."""
},
{
    "kb_id": 'KB-107',
    "title": 'Reporting Suspicious Emails and Phishing Attempts',
    "category": 'Security',
    "tags": ['Security', 'Phishing', 'Email'],
    "last_updated": '2026-07-12',
    "priority": 'Low',
    "version": '1.3',
    "author": 'Security Team',
    "content": """Overview
This guide explains how to identify and report phishing emails in order to protect your account and company data. Phishing remains one of the most common ways attackers gain initial access to corporate systems, and the speed at which a suspicious email is reported often determines how contained the resulting incident is. Every employee plays a role in this first line of defense, regardless of technical background.

Symptoms
Suspicious emails often contain urgent or threatening language demanding immediate action, such as claims that an account will be closed within hours unless credentials are confirmed. They frequently include requests for login credentials or payment information sent through email rather than a secure portal, unexpected attachments from senders you were not expecting to hear from, or sender addresses that closely mimic legitimate contacts with subtle misspellings that are easy to miss at a glance. Some phishing attempts are highly targeted and reference real internal projects or colleagues, making them harder to spot than generic scam emails.

Troubleshooting Steps
Never click links or download attachments from emails you were not expecting to receive, even if they appear to come from a known contact, since sender addresses can be spoofed or a genuine contact's account may itself be compromised. Hover over links without clicking to preview the actual destination URL shown at the bottom of most email clients, and compare it carefully against the domain you would expect. Check the sender's full email address rather than just the display name, since attackers frequently spoof a familiar display name while using a completely different underlying address. If you have already clicked a suspicious link or entered credentials, disconnect from the network immediately rather than continuing to investigate on your own, since time matters more than gathering additional details at that point.

Resolution
Use the Report Phishing button available in your email client to forward suspicious messages directly to the security team for analysis, which also removes the message from your inbox safely. If you entered credentials on a suspicious page, change your password immediately through a separate, trusted device and notify security right away, as your account may require additional monitoring or a forced credential rotation depending on what was exposed."""
},
{
    "kb_id": 'KB-108',
    "title": 'Wireless Network Connectivity Issues',
    "category": 'Networking',
    "tags": ['WiFi', 'Network', 'Connectivity'],
    "last_updated": '2026-06-25',
    "priority": 'High',
    "version": '1.0',
    "author": 'Network Team',
    "content": """Overview
This article covers troubleshooting steps for employees experiencing unstable or unavailable WiFi connections in the office. Office wireless networks serve dozens or hundreds of devices simultaneously, and connectivity issues can stem from the individual device, a specific access point, or the broader network infrastructure, so identifying which category applies is the first step toward a fast resolution.

Symptoms
Devices may fail to detect the office wireless network entirely despite it being visible to colleagues nearby, connect successfully but show a limited connectivity warning with no actual internet access, or experience frequent disconnections throughout the day at seemingly random intervals. Some employees notice the issue is worse in specific areas of the building, which is a useful clue for diagnosis.

Troubleshooting Steps
Toggle WiFi off and on from your device settings to force a fresh rescan for available networks, which resolves a surprising number of detection issues on its own. Forget the network entirely on your device and reconnect using fresh credentials, since saved network profiles can occasionally become corrupted after a password change or configuration update on the network side. Move closer to a known access point if you are in an area with historically weak coverage, such as stairwells, basements, or rooms with significant physical obstruction. Restart your device's network adapter through device manager if disconnections persist after reconnecting normally, as this clears a lower-level driver state that a simple toggle does not always reach.

Resolution
If multiple users in the same physical area report connectivity issues at the same time, this strongly indicates an access point failure rather than an individual device problem, and should be reported to network administration with the specific location and approximate time the issue began. Isolated single-device issues that persist after all steps above should be reported with the device model and operating system version, as certain hardware and driver combinations are more prone to specific wireless issues than others."""
},
{
    "kb_id": 'KB-109',
    "title": 'Multi-Factor Authentication Setup and Issues',
    "category": 'Security',
    "tags": ['Security', 'MFA', 'Authentication'],
    "last_updated": '2026-07-08',
    "priority": 'Medium',
    "version": '1.1',
    "author": 'Security Team',
    "content": """Overview
This guide covers setting up multi-factor authentication and resolving the most common issues when authentication codes fail to work as expected. MFA is a required security control across all company systems, and while it significantly reduces the risk of account compromise, a small number of predictable configuration issues account for the large majority of support requests related to it.

Symptoms
The authenticator app may fail to generate valid codes at all, codes may be rejected as expired immediately after being generated with no visible delay, or SMS-based codes may simply never arrive despite the phone number appearing correct in the account settings. Some users report the app working fine for weeks and then suddenly failing after an update to their phone's operating system.

Troubleshooting Steps
Confirm the time on your mobile device is set to automatic and synced correctly, as authenticator apps rely on precise time matching between your device and the authentication server, and even a small clock drift is enough to invalidate every generated code. If codes are consistently rejected despite correct time settings, remove and re-add the account within your authenticator app entirely, which regenerates the underlying secret key rather than attempting to reuse a potentially corrupted one. For SMS-based codes specifically, confirm your registered phone number is current and correctly formatted in the employee portal, since even a single incorrect digit will cause silent delivery failure with no error shown to the user.

Resolution
Time synchronization issues resolve immediately once automatic time is enabled and the device has had a moment to resync with the network time server. If you have lost access to your authenticator device entirely, whether through loss, theft, or a factory reset, contact IT security directly for identity verification and account recovery, as this specific scenario cannot be self-serviced for security reasons and requires manual verification of your identity through an alternate channel."""
},
{
    "kb_id": 'KB-110',
    "title": 'Printer Connectivity and Print Queue Issues',
    "category": 'Hardware',
    "tags": ['Hardware', 'Printer'],
    "last_updated": '2026-06-18',
    "priority": 'Low',
    "version": '1.2',
    "author": 'Hardware Support Team',
    "content": """Overview
This article addresses common printer issues including failure to print, stuck print queues, and connectivity problems affecting shared office printers. Because printers are typically shared across many employees, a single stuck job or configuration issue can quietly affect everyone in a department, making quick diagnosis particularly valuable.

Symptoms
Print jobs may appear stuck in the queue indefinitely with no visible progress or error, the printer may show as offline in the system despite clearly being powered on and connected to the network, or documents may print successfully but with formatting errors such as incorrect margins or missing images. Some users notice that only their own jobs are affected while colleagues print normally, which is a useful signal that the issue is local rather than printer-wide.

Troubleshooting Steps
Clear the print queue completely and resend the job rather than attempting to resume a stuck one, since stuck jobs frequently block all subsequent print requests from that device until manually cleared. Confirm the printer is on the same network as your device, particularly after any recent network changes or if you have switched between office locations, since printers are often configured for a specific subnet. Restart the print spooler service on your machine, which resolves the majority of queue-related freezes without requiring any changes to the printer itself. Update or reinstall the printer driver if formatting errors persist across multiple different documents, since a corrupted or outdated driver is the most common cause of this specific symptom.

Resolution
Most queue issues resolve after clearing stuck jobs and restarting the print spooler, which together resolve the large majority of reported cases without further escalation. If the printer remains offline after completing these steps, check the physical network cable or WiFi connection on the printer itself, as hardware-level disconnection on the printer's side is a common root cause that is easy to overlook when troubleshooting only from the computer."""
},
{
    "kb_id": 'KB-111',
    "title": 'Setting Up Company Email on Mobile Devices',
    "category": 'Email',
    "tags": ['Email', 'Mobile', 'iPhone', 'Android', 'Setup'],
    "last_updated": '2026-07-20',
    "priority": 'Medium',
    "version": '1.0',
    "author": 'Collaboration Tools Team',
    "content": """Overview
This article explains how to set up company email on a personal or company mobile device, covering both iPhone and Android. Mobile email setup is one of the most common onboarding requests, and it also comes up whenever an employee changes phones, so knowing the correct process avoids repeated support tickets.

Symptoms
Employees setting up mobile email often report a certificate error partway through configuration, the account appearing to add successfully but never syncing any messages, or repeated password prompts even after entering the correct credentials. On Android specifically, some users cannot find the correct server settings, while on iPhone the built-in Mail app may accept the account but silently fail to pull new mail. A common thread is that everything looks configured but no email actually arrives.

Troubleshooting Steps
Use the official company email app rather than the device's built-in mail client wherever possible, since the official app handles security certificates and server settings automatically and avoids most manual configuration errors. Enter your full email address as the username, not just the part before the at sign, since a partial username is a frequent cause of silent authentication failures. If the device prompts for server settings manually, use the documented company mail server address rather than guessing, and confirm the account type matches what IT specifies. If multi-factor authentication is enabled on your account, complete the additional verification step when prompted rather than dismissing it, as an incomplete MFA step leaves the account added but unable to sync.

Resolution
Most mobile setup issues resolve by using the official app and entering the full email address as the username. If the device still fails to sync after these steps, it may require mobile device management enrollment before corporate email is permitted, which IT can complete. Certificate errors that persist after using the official app should be reported, since they usually indicate the device needs an updated security profile pushed from IT rather than any change the employee can make themselves."""
},
{
    "kb_id": 'KB-112',
    "title": 'Application Crashing or Freezing Repeatedly',
    "category": 'Software',
    "tags": ['Software', 'Crash', 'Freeze', 'Performance'],
    "last_updated": '2026-07-20',
    "priority": 'Medium',
    "version": '1.0',
    "author": 'Application Support Team',
    "content": """Overview
This guide covers what to do when a specific application repeatedly crashes on launch, freezes during use, or becomes unresponsive when handling larger files. These issues are distinct from licensing or installation problems, since the application is installed and starting but failing during actual use, and they are among the most disruptive because they interrupt work already in progress.

Symptoms
Employees typically report an application closing itself without warning shortly after opening, freezing when a particular action is taken such as opening a large file or joining a call, or becoming progressively slower until it stops responding entirely. Some notice the problem only appears with larger documents or longer sessions, while smaller tasks work normally. Others find the crash happens only on their machine while colleagues using the same application are unaffected, which points to a local cause rather than a fault in the application itself.

Troubleshooting Steps
Close the application fully and reopen it, confirming it is not still running in the background, since a partially closed process can prevent a clean restart. Check available system memory and close other resource-heavy applications, because crashes when handling large files are frequently caused by the machine running out of memory rather than an application bug. Clear the application's cache or temporary files if it offers that option, since a corrupted cache commonly causes freezes that survive a simple restart. Confirm the application is updated to the latest approved version, as many stability problems are already fixed in a newer release. Note whether the crash is tied to one specific action, since that detail significantly narrows the cause.

Resolution
Most repeated crashes resolve after clearing the cache, freeing up memory, and updating to the latest version. If the application continues to crash on a specific reproducible action, report it with the exact steps that trigger it and the application version, since a reproducible crash is far faster for the support team to diagnose. Persistent crashes isolated to one machine may indicate a corrupted installation that needs a clean reinstall rather than further troubleshooting."""
},
{
    "kb_id": 'KB-113',
    "title": 'Requesting Access to HR and Payroll Systems',
    "category": 'Human Resources',
    "tags": ['HR', 'Payroll', 'Access', 'Accounts'],
    "last_updated": '2026-07-20',
    "priority": 'Medium',
    "version": '1.0',
    "author": 'IT Service Desk',
    "content": """Overview
This article explains how employees request access to HR and payroll self-service systems, and clarifies which requests IT can handle versus which must be routed to the HR department directly. This distinction matters because employees frequently raise HR questions as IT tickets, and knowing where each type belongs avoids tickets bouncing between teams and getting delayed.

Symptoms
Employees often submit IT tickets asking how to update personal details such as direct deposit banking information, how to request additional leave, or where to submit an expense reimbursement claim. In these cases the issue is not a technical fault at all but a question about an HR process. A genuinely technical version of these requests looks different: being unable to log in to the HR portal, the portal not loading, or an access-denied error when opening a page the employee should be able to reach.

Troubleshooting Steps
First determine whether the request is about access or about a process. If the employee simply cannot reach the HR portal or gets a login or access-denied error, that is an IT access issue: confirm the account is active, verify the employee has been granted the correct HR system role, and reset credentials if needed. If instead the request is about how to perform an HR task such as changing banking details or requesting leave, this is an HR process question and should be routed to the HR department, since IT does not own or modify payroll and leave data. When in doubt, confirm with the employee whether they cannot access the system or simply do not know the process.

Resolution
Technical access issues to the HR portal are resolved by confirming the account role and resetting access as needed. Process questions about payroll, leave, or reimbursements are handed off to the HR department, who own those systems and policies. Making this routing clear up front is the fastest resolution, since it avoids the common delay of an HR process question sitting in the IT queue before being redirected."""
},
{
    "kb_id": 'KB-114',
    "title": 'Software Update and Patch Installation Issues',
    "category": 'Software',
    "tags": ['Software', 'Update', 'Patch', 'Installation'],
    "last_updated": '2026-07-20',
    "priority": 'Low',
    "version": '1.0',
    "author": 'Application Support Team',
    "content": """Overview
This article covers problems that occur when an application or system update fails to install, gets stuck partway, or repeatedly reoffers itself after appearing to complete. Keeping software patched is important for both security and stability, so update failures matter beyond just the immediate inconvenience, and resolving them promptly keeps devices compliant.

Symptoms
Employees report an update that starts but fails partway with an error, an application that will not launch after an interrupted update, or the same update being offered again and again despite appearing to install successfully. Some updates appear to hang indefinitely with no visible progress, while others fail only when disk space is low. A useful signal is whether the failure happens at the same point each time, which suggests a specific cause rather than a transient glitch.

Troubleshooting Steps
Restart the device and retry the update, since a pending restart from a previous update frequently blocks a new one from completing. Confirm there is sufficient free disk space, as updates that fail near completion are often simply running out of room to unpack files. Clear the update cache if the same update keeps reoffering, since a corrupted downloaded update package causes exactly this repeating behaviour. Ensure the device stays connected to power and network throughout the update rather than going to sleep midway, because an interrupted update is a common cause of an application that will not launch afterward. Confirm you have the permissions the update requires, since some updates need administrator rights.

Resolution
Most update failures resolve after a restart, freeing disk space, and clearing the update cache. If an application will not launch after a failed update, it may need a repair or clean reinstall rather than another update attempt. Report a persistently failing update with the exact error message and the application version, since the specific failure point usually identifies the cause quickly."""
},
{
    "kb_id": 'KB-115',
    "title": 'Account Onboarding and Offboarding Requests',
    "category": 'Human Resources',
    "tags": ['HR', 'Onboarding', 'Offboarding', 'Accounts', 'Access'],
    "last_updated": '2026-07-20',
    "priority": 'Medium',
    "version": '1.0',
    "author": 'IT Service Desk',
    "content": """Overview
This article explains how account setup for new hires and account removal for departing employees are handled, and what the requesting manager or employee needs to provide. Onboarding and offboarding sit at the boundary between HR and IT, so a clear process prevents both the delay of a new hire waiting on access and the security risk of a departed employee retaining it.

Symptoms
Common requests include a new employee needing accounts, email, and system access set up before their start date, a manager asking why a new hire cannot yet log in, or a request to disable access for someone who has left or is about to leave. A frequent problem is a request arriving with incomplete information, such as missing the start date, role, or which systems the person needs, which stalls the setup.

Troubleshooting Steps
For onboarding, confirm the request includes the new employee's full name, start date, role or department, and the specific systems and access level required, since setup cannot be completed accurately without these. Verify the request came from an authorized manager, as account creation requires proper approval. For offboarding, confirm the employee's last working day and whether access should be disabled immediately or on a scheduled date, and identify any shared accounts or data that need to be reassigned before their account is removed. Treat urgent offboarding, such as an immediate departure, as time-sensitive because retained access after departure is a genuine security concern.

Resolution
Onboarding requests are completed once all required details and manager approval are confirmed, ideally ahead of the start date so the new hire can log in on day one. Offboarding requests disable access on the agreed date and reassign any shared data or mailboxes first. Because these requests involve both HR records and IT systems, the fastest resolution comes from HR and IT coordinating on the employee's details rather than handling their parts in isolation."""
},
{
    "kb_id": 'KB-116',
    "title": 'Bluetooth Device Not Connecting or Pairing',
    "category": 'Hardware',
    "tags": ['Hardware', 'Bluetooth', 'Pairing', 'Wireless', 'Peripherals'],
    "last_updated": '2026-07-22',
    "priority": 'Low',
    "version": '1.0',
    "author": 'Hardware Support Team',
    "content": """Overview
This article explains how to resolve problems connecting Bluetooth devices such as wireless headsets, mice, keyboards, and speakers to a work laptop. Bluetooth issues are common because they involve two devices that both have to be in the right state at the same time, and a small mismatch on either side prevents a connection, so a clear step-by-step approach saves a lot of trial and error.

Symptoms
Employees typically report a Bluetooth device that will not appear in the list of available devices to pair, a device that pairs successfully but then repeatedly disconnects during use, or a device that connects but produces no sound or input. Some notice the device works on their phone but not their laptop, which points to the laptop's Bluetooth configuration rather than a faulty device. Others find the device connected in settings but not actually working, which usually means it paired to a different nearby machine.

Troubleshooting Steps
Confirm Bluetooth is switched on for the laptop and that the device itself is powered on and in pairing mode, since most wireless peripherals only advertise themselves for a short window after pairing mode is activated. If the device does not appear, move it closer and away from other wireless devices, as interference and distance are frequent causes of a device failing to show up. If the device previously paired but now will not reconnect, remove or forget it in Bluetooth settings and pair it again fresh, which clears a stale or corrupted pairing. Replace the batteries in the device if it is battery powered, since low power often causes both failure to pair and repeated disconnections. Confirm the device is not still connected to another nearby machine, since most peripherals only connect to one host at a time.

Resolution
Most Bluetooth issues resolve by toggling Bluetooth, putting the device back into pairing mode, and removing then re-adding the pairing. If a device pairs but still will not work after these steps, test it on another machine to determine whether the fault is the device or the laptop's Bluetooth adapter. A device that fails across multiple machines needs replacing, while one that works elsewhere but not on the work laptop should be reported so the laptop's Bluetooth adapter or drivers can be checked."""
},
{
    "kb_id": 'KB-117',
    "title": 'Keyboard Not Responding or Missing Keystrokes',
    "category": 'Hardware',
    "tags": ['Hardware', 'Keyboard', 'Input', 'Peripherals'],
    "last_updated": '2026-07-22',
    "priority": 'Medium',
    "version": '1.0',
    "author": 'Hardware Support Team',
    "content": """Overview
This article covers what to do when a keyboard stops responding entirely, misses keystrokes, or types the wrong characters. Because the keyboard is essential to almost all work, even a partial failure is highly disruptive, so this guide helps quickly determine whether the cause is software, a connection problem, or a genuine hardware fault requiring replacement.

Symptoms
Employees report a keyboard that has become completely unresponsive with no keys registering, specific keys that no longer work while the rest function normally, or keys that produce the wrong character or repeat unexpectedly. Some notice the problem appears only in one application, which points to a software or settings cause rather than the keyboard itself. Others find an external keyboard fails while the built-in laptop keyboard still works, which helps isolate where the fault lies.

Troubleshooting Steps
Restart the device first, since a full restart clears the majority of temporary input glitches that cause a keyboard to stop responding. For an external keyboard, reseat the cable or, for a wireless model, check the batteries and the receiver, as a loose connection or low power is a common cause. Test the behaviour in more than one application to determine whether the issue is system-wide or limited to a single program, since an application-specific issue is not a keyboard fault. Check for stuck keys or debris under keys that are not registering, and confirm the correct keyboard language and layout are selected, since a wrong layout is a frequent cause of keys typing the wrong character. Connect a known-good external keyboard to test whether the laptop still accepts input at all.

Resolution
Most keyboard issues resolve after a restart, reseating the connection, or correcting the layout setting. If specific keys consistently fail while an external keyboard works normally, the built-in keyboard likely has a hardware fault and should be reported for repair or replacement. If no keyboard works at all, including a known-good external one, the issue is deeper than the keyboard and needs hardware support to inspect the device."""
},
]

def get_articles():
    return articles