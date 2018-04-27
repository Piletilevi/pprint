# Versioning and release management

Semantic versioning is required.

Code is released as tags prefixed by major and minor i.e. `0.2-pprint`.  
Tag could be moved to different commit as needed.



## To create a new release

1. Commit all changes for new release
2. Increment version number in \_version.py
3. Commit version increment with message `Release major.minor.patch`
4. Create a release (copy content from previous one and update where relevant)
5. Update and commit README.md to refer to new release
