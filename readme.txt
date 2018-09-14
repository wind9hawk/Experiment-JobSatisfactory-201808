Release 4, Dataset 2 Notes

Major Changes
* Content is integrated with the graph structure.
* A user's topics of interest can drift over time.
* Email now includes CC/BCC.
* Email table now includes user ID and PC.
* Users can have one or more non-work email addresses.
* A latent job satisfaction variable was added. It might make sense for us to specify exactly how this affects observable variables, so let us know if that information is desired.
* An additional red team scenario was added. (All previous red team scnearios also occur in the dataset.)
* This is a "dense needles" dataset. There is an unrealistically high amount of red team data interspersed.


license.txt
* ExactData license information


logon.csv
* Fields: id, date, user, pc, activity (Logon/Logoff)
* Weekends and statutory holidays (but not personal vacations) are included as days when fewer people work.
* No user may log onto a machine where another user is already logged on, unless the first user has locked the screen.
* Logoff requires preceding logon
* A small number of daily logons are intentionally not recorded to simulate dirty data.
* Some logons occur after-hours
  - After-hours logins and after-hours thumb drive usage are intended to be significant.
* Logons precede other PC activity
* Screen unlocks are recorded as logons. Screen locks are not recorded.
* Any particular user’s average habits persist day-to-day
  - Start time (+ a small amount of variance)
  - Length of work day (+ a small amount of variance)
  - After-hours work: some users will logon after-hours, most will not
* Some employees leave the organization:  no new logon activity from the default start time on the day of termination
* 1k users, each with an assigned PC
* 100 shared machines used by some of the users in addition to their assigned PC. These are shared in the sense of a computer lab, not in the sense of a Unix server or Windows Terminal Server.
* Systems administrators with global access privileges are identified by job role "ITAdmin".
* Some users log into another user's dedicated machine from time to time.


device.csv
* Fields: id, date, user, pc, activity (connect/disconnect)
* Some users use a thumb drive
* Some connect events may be missing disconnect events, because users can power down machine before removing drive
* Users are assigned a normal/average number of thumb drive uses per day. Deviations from a user's normal usage can be considered significant.


http.csv
* Fields: id, date, user, pc, url, content
* Has modular/community structure, but is not correlated with social/email graph.
* Domain names have been expanded to full URLs with paths.
* Words in the URL are usually related to the topic of the web page.
* Content consists of a space-separated list of content keywords.
* Each web page can contain multiple topics.
* WARNING: Most of the domain names are randomly generated, so some may point to malicious websites. Please exercise caution if visiting any of them.


email.csv
* Fields: id, date, user, pc, to, cc, bcc, from, size, attachment_count, content
* Driven by underlying friendship and organizational graphs.
* Role (from LDAP) drives the amount of email a user sends per day.
* The vast majority of edges (sender/recipient pairs) are exist because the two users are friends.
* A small number of edges are introduced as noise. A small percentage of the time, a user will email someone randomly.
* Emails can have multiple recipients
* Emails can have a mix of employees and non-employees in dist list
* Non employees use a non-DTAA email addresses; employees use a DTAA email address
* Terminated employees remain in the population, and thus are eligible to be contacted as non-employees
* A friendship graph edge is not implied between the multiple recipients of an email.
* Unlike the previous release, we do not believe the observed email graph follows graph power laws
  because the power-law-conforming friendship graph is overwhelmed by the organizational graph.
* Email size and attachment count are not correlated with each other.
* Email size refers to the number of bytes in the message, not including attachments.
* Content consists of a space-separated list of content keywords.
* "Content" does not specifically refer to the subject or body. We have not made that distinction.
* Each message can contain multiple topics.
* Message topics are chosen based on both sender and recipient topic affinities.


file.csv
Fields: id, date, user, pc, filename, content
* Each entry represents a file copy to a removable media device.
* Content consists of a hexadecimal encoded file header followed by a space-separated list of content keywords
* Each file can contain multiple topics.
* File header correlates with filename extension.
* The file header is the same for all MS Office file types.
* Each user has a normal number of file copies per day. Deviation from normal can be considered a significant indicator.


psychometric.csv
* Fields: employee_name, user_id, O, C, E, A, N
* Big 5 psychometric score
* See http://en.wikipedia.org/wiki/Big_Five_personality_traits for the definitions of O, C, E, A, N ("Big 5").
* Extroversion score drives the number of connections a user has in the friendship graph.
* Conscientiousness score drives late work arrivals.
* This information would be latent in a real deployment, but is offered here in case it is helpful.
* A latent job satisfaction variable drives some behaviors.

Malicious actors
* This data contains two instances of insider threats.
* Data dimensions that are fair game for anomaly detection (not all are used in red team scenarios)
  - In general, radical changes in behavior
  - Unusual logon times (for that user)
  - Unusual logins to another user's dedicated machine (for users that don't do this normally)
  - Device usage for users who aren't normally device users, or increased device usage for those that are.
  - Radical increases in the amount of device usage by a user
  - Employee termination (as an indicator, but not anomaly detection per se)
  - Number of emails sent / day
  - Change in web browsing habits (visits to unusual websites are interesting, but also common)
  - Radical change in social graph behavior (unexpected email recipients, perhaps)
  - Topics of web sites visited, emails, and files copied.
* We can reveal as much as you would like about the red team scenarios.
* This is a "dense needles" dataset. There is an unrealistically high amount of red team data interspersed.

Errata:
* Field Ids are unique within a csv file (logon.csv, device.csv) but may not be globally unique.
