# Changelog

All notable changes to Unthinking Majority's website will be documented in this file.

The format of this document is loosely based on [Keep a Changelog](https://keepachangelog.com/).

# 2023-10-27

### Changed

* Expiration period for Dragonstone submissions is now configurable via the DRAGONSTONE_EXPIRATION_PERIOD object in the
  Settings admin
* Authenticated users no longer need to fill out user field for solo submissions
* Achievements and Dragonstone models now utilize django polymorhpic
    * Admin interfaces for both should look much cleaner now!

### Added

* Preferred name features for users
    * Preferred names will now be displayed in place of the user in game name if available
    * User can change their preferred name by going to their profile page and following the link from there

### Fixed
