describe('admin configure network settings', function() {
  it('should enable whistleblowers over https', function() {
    browser.setLocation('admin/network');

    element.all(by.model('admin.node.hostname')).get(0).clear().sendKeys('localhost');
    element(by.model('admin.node.onionservice')).clear().sendKeys('1234567890123456.onion');

    element.all(by.cssContainingText("button", "Save")).get(0).click();

    // grant tor2web permissions
    element(by.cssContainingText("a", "Access control")).click();

    expect(element(by.model('admin.node.tor2web_whistleblower')).isSelected()).toBeFalsy();
    element(by.model('admin.node.tor2web_whistleblower')).click();

    // save settings
    element.all(by.id("AccessControlSave")).click().then(function() {
      expect(element(by.model('admin.node.tor2web_whistleblower')).isSelected()).toBeTruthy();
    });
  });
});

describe('admin configure https', function() {
  var files = {
    priv_key: browser.gl.utils.makeTestFilePath('../../../../backend/globaleaks/tests/data/https/valid/priv_key.pem'),
    cert: browser.gl.utils.makeTestFilePath('../../../../backend/globaleaks/tests/data/https/valid/cert.pem'),
    chain: browser.gl.utils.makeTestFilePath('../../../..//backend/globaleaks/tests/data/https/valid/chain.pem'),
  };

  it('should interact with all ui elements', function() {
    browser.setLocation('admin/network');
    element(by.cssContainingText("a", "HTTPS settings")).click();

    element(by.cssContainingText("button", "Proceed")).click();

    element(by.id("HTTPSAutoMode")).click()

    element(by.cssContainingText("button", "Cancel")).click();

    element(by.cssContainingText("button", "Proceed")).click();

    element(by.id("HTTPSManualMode")).click()

    var pk_panel = element(by.css('div.panel.priv-key'));
    var csr_panel = element(by.css('div.panel.csr'));
    var cert_panel = element(by.css('div.panel.cert'));
    var chain_panel = element(by.css('div.panel.chain'));
    var modal_action = by.id('modal-action-ok');

    // Generate key
    pk_panel.element(by.cssContainingText('button', 'Generate')).click();

    // Generate csr
    element(by.id('csrGen')).click();

    var csr_panel = element(by.css('div.panel.csr'));
    csr_panel.element(by.model('csr_cfg.country')).sendKeys('IT');
    csr_panel.element(by.model('csr_cfg.province')).sendKeys('Liguria');
    csr_panel.element(by.model('csr_cfg.city')).sendKeys('Genova');
    csr_panel.element(by.model('csr_cfg.company')).sendKeys('Internet Widgets LTD');
    csr_panel.element(by.model('csr_cfg.department')).sendKeys('Suite reviews');
    csr_panel.element(by.model('csr_cfg.email')).sendKeys('nocontact@certs.may.hurt');
    element(by.id('csrSubmit')).click();

    // Download csr
    if (browser.gl.utils.testFileDownload()) {
      csr_panel.element(by.id('downloadCsr')).click();
    }

    // Delete csr
    element(by.id('deleteCsr')).click();
    browser.gl.utils.waitUntilPresent(modal_action);
    element(modal_action).click();
    browser.wait(protractor.ExpectedConditions.stalenessOf(element(by.id('deleteCsr'))));

    // Delete key
    element(by.id('deleteKey')).click();
    browser.gl.utils.waitUntilPresent(modal_action);
    element(modal_action).click();
    browser.wait(protractor.ExpectedConditions.stalenessOf(element(by.id('deleteKey'))));

    element(by.cssContainingText("button", "Proceed")).click();

    element(by.id("HTTPSManualMode")).click()

    if (browser.gl.utils.testFileUpload()) {
      // Upload key
      browser.executeScript('angular.element(document.querySelectorAll(\'div.panel.priv-key input[type="file"]\')).attr("style", "display: block; visibility: visible")');
      element(by.id("keyUpload")).sendKeys(files.priv_key);

      // Upload cert
      browser.executeScript('angular.element(document.querySelectorAll(\'div.panel.cert input[type="file"]\')).attr("style", "display: block; visibility: visible")');
      element(by.id("certUpload")).sendKeys(files.cert);

      // Upload chain
      browser.executeScript('angular.element(document.querySelectorAll(\'div.panel.chain input[type="file"]\')).attr("style", "display: block; visibility: visible")');
      element(by.id("chainUpload")).sendKeys(files.chain);

      // Download the cert and chain
      if (browser.gl.utils.testFileDownload()) {
        cert_panel.element(by.id('downloadCert')).click();
        chain_panel.element(by.id('downloadChain')).click();
      }

      // Delete chain, cert, key
      chain_panel.element(by.id('deleteChain')).click();
      element(modal_action).click();

      cert_panel.element(by.id('deleteCert')).click();
      browser.gl.utils.waitUntilPresent(modal_action);
      element(modal_action).click();

      pk_panel.element(by.id('deleteKey')).click();
      browser.gl.utils.waitUntilPresent(modal_action);
      element(modal_action).click();
    }
  });
});