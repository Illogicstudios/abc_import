# ABC Import

ABC Import is a tool to import ABCs with versioning.

It pairs up with the ABC Export tool (https://github.com/Illogicstudios/abc_export)
and it requires the Look Loader tool (https://github.com/Illogicstudios/look_loader)

## How to install

You will need some files that several Illogic tools need. You can get them via this link :
https://github.com/Illogicstudios/common

---

## Features

### Retrieve Anims and Furs

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/219347243-0525e34d-dcf6-425d-8c7c-8554ac32bd87.png" width=30%>
  </span>
  <p weight="bold">Example of the file architecture built from the ABC Export tool that can be retrived with the ABC Import</p>
  <br/>
</div>

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/220320877-7e1d392a-8c96-4b58-9a08-ce97dc6f7c4c.png" width=60%>
  </span>
  <p weight="bold">You can retrieve the abc anim and the abc fur from a folder</p>
  <br/>
</div>

A valid folder is an existing folder named "abc" or "abc_fur" or the parent folder of one of these.

In the User interface you can visualize the available versions and if the assets are already in the scene. Here no assets are present.

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/220321933-3446ffe5-19fd-43bb-90c3-50a0fa062539.png" width=60%>
  </span>
  <p weight="bold">States change when assets are already in the scene</p>
  <br/>
</div>

### Importing and Updating

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/220323225-26d0028d-0456-4560-986b-65034b7d6f06.png" width=45%>
  </span>
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/220323284-f07ec8e0-4f87-41f7-8e42-ea8572495964.png" width=45%>
  </span>
  <p weight="bold">Updating the version of an abc</p>
  <br/>
</div>

By selecting a row and clicking the button "Import or Update selection" the abc will be update or import to the version selected in the "Import version" of the abc.

The "Update look" buttons updates the uvs and shaders of animations and shaders of furs independently of the import version.

The checkbox "Update UVs and Shaders" achieve the same goal that the "Update looks" buttons but at the import or update of the abc.

